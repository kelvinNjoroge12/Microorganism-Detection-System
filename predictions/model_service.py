import os
import tensorflow as tf
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import h5py
import json
from django.core.files.storage import default_storage
from django.conf import settings
from tensorflow.keras.utils import custom_object_scope
from .models import ModelVersion

logger = logging.getLogger(__name__)


class FixedDropout(tf.keras.layers.Dropout):
    """Proper implementation of FixedDropout layer"""

    def __init__(self, rate, **kwargs):
        super().__init__(rate, **kwargs)
        self._rate = rate

    def get_config(self):
        config = super().get_config()
        config.update({'rate': self._rate})
        return config


class AIClassifier:
    def __init__(self):
        # Initialize TensorFlow settings first
        self._initialize_tf()
        self.model = None
        self.current_model_version = None
        self.class_names = []
        self.confidence_threshold = 0.7
        self.model_input_size = (380, 380)
        self.metadata = {}

    def _initialize_tf(self):
        """Configure TensorFlow environment"""
        # Reduce verbosity of TensorFlow logs
        tf.get_logger().setLevel('ERROR')
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

        # For debugging, you can force CPU-only mode
        # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        # Clean up any existing sessions
        tf.keras.backend.clear_session()

    def load_model(self):
        """Enhanced model loading with better error handling"""
        try:
            self._clear_model()

            # Get active model with proper Django ORM query
            active_model = ModelVersion.objects.filter(is_active=True).first()
            if not active_model:
                logger.error("No active model in database")
                return False
            if not active_model.model_file:
                logger.error("Active model has no file associated")
                return False

            # Get absolute path in Django context
            try:
                model_path = active_model.model_file.path
                if not os.path.exists(model_path):
                    logger.error(f"Model file not found at: {model_path}")
                    return False
            except Exception as e:
                logger.error(f"Path resolution error: {str(e)}")
                return False

            # Define custom objects
            custom_objects = {'FixedDropout': FixedDropout}

            try:
                # Clear any existing TensorFlow session
                tf.keras.backend.clear_session()

                # Load model with custom objects
                with custom_object_scope(custom_objects):
                    self.model = tf.keras.models.load_model(model_path, compile=False)

                    # Load metadata
                    self._load_metadata(model_path)

                    self.current_model_version = active_model.version
                    logger.info(f"Successfully loaded model: {active_model.version}")
                    return True

            except Exception as e:
                logger.error(f"Model loading failed: {str(e)}", exc_info=True)
                return False

        except Exception as e:
            logger.error(f"Unexpected error in load_model: {str(e)}", exc_info=True)
            return False

    def _load_metadata(self, model_path):
        """Load metadata from model file"""
        try:
            with h5py.File(model_path, 'r') as h5file:
                for key in h5file.attrs.keys():
                    if key == 'model_config':  # Skip internal TF attributes
                        continue
                    try:
                        value = h5file.attrs[key]
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                pass
                        self.metadata[key] = value
                    except Exception as e:
                        logger.warning(f"Couldn't load metadata {key}: {str(e)}")

            # Update model properties from metadata
            if 'image_size' in self.metadata:
                self.model_input_size = tuple(self.metadata['image_size'])
            if 'class_names' in self.metadata:
                self.class_names = self.metadata['class_names']
            if 'confidence_threshold' in self.metadata:
                self.confidence_threshold = float(self.metadata['confidence_threshold'])

        except Exception as e:
            logger.error(f"Metadata loading failed: {str(e)}")

    def preprocess_image(self, image_bytes):
        """Improved image preprocessing with better error handling"""
        try:
            img = Image.open(BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img = img.resize(self.model_input_size)
            img_array = np.array(img, dtype=np.float32) / 255.0
            return np.expand_dims(img_array, axis=0)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}", exc_info=True)
            raise ValueError(f"Invalid image: {str(e)}")

    def predict(self, image_bytes):
        """Robust prediction method with detailed error reporting"""
        if not self.model:
            logger.error("Prediction attempt with unloaded model")
            return {
                'success': False,
                'error': "Model not properly loaded. Please check admin panel.",
                'confidence': 0.0
            }

        try:
            processed_img = self.preprocess_image(image_bytes)
            predictions = self.model.predict(processed_img, verbose=0)
            result = self._process_predictions(predictions)

            logger.debug(f"Raw prediction result: {result}")

            if result['confidence'] < self.confidence_threshold:
                return {
                    'success': False,
                    'error': f"Low confidence prediction ({result['confidence']:.2%})",
                    'confidence': result['confidence'],
                    'microorganism': result['microorganism'],
                    'full_name': result['full_name'],  # Add this
                    'is_harmful': result['is_harmful'],
                    'food_source': result['food_source']
                }

            return {
                'success': True,
                'microorganism': result['microorganism'],
                'full_name': result['full_name'],  # Add this
                'confidence': result['confidence'],
                'is_harmful': result['is_harmful'],
                'food_source': result['food_source']
            }

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Prediction error: {str(e)}",
                'confidence': 0.0,
                'show_popup': True,
                'popup_duration': 120000,
                'popup_message': "Could not process image"
            }

    def _process_predictions(self, predictions):
        pred_idx = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))
        full_name = self.class_names[pred_idx] if self.class_names else str(pred_idx)

        # Initialize default values
        microorganism = full_name
        is_harmful = False
        food_source = "Unknown"

        # Parse the full name according to your format:
        # "Spherical_bacteria_1_Contaminated dairy products, raw meat, vegetables, seafood, unpasteurized juices"
        if "_" in full_name:
            parts = full_name.split("_")
            microorganism = parts[0]  # First part is the microorganism name

            # Check if harmful (1_ in the name)
            if len(parts) > 2 and parts[2] == "1":
                is_harmful = True

            # Extract food sources (everything after "Contaminated")
            if len(parts) > 3 and "Contaminated" in parts[3]:
                food_source = parts[3].split("Contaminated")[-1].strip()
            elif len(parts) > 3:
                food_source = parts[3]

        return {
            'microorganism': microorganism,
            'full_name': full_name,  # Add this to keep the full original name
            'confidence': confidence,
            'is_harmful': is_harmful,
            'food_source': food_source
        }

    def _determine_food_source(self, microorganism, confidence):
        """Enhanced food source determination logic"""
        # Add your custom logic here based on microorganism type
        return "Unknown"  # Replace with your implementation

    def _clear_model(self):
        """Thorough cleanup of model resources"""
        if self.model:
            try:
                tf.keras.backend.clear_session()
                del self.model
            except Exception as e:
                logger.warning(f"Error clearing model: {str(e)}")

        self.model = None
        self.current_model_version = None
        self.class_names = []
        self.metadata = {}

    def get_status(self):
        """Detailed model status report"""
        active_model = ModelVersion.objects.filter(is_active=True).first()
        return {
            'loaded': self.model is not None,
            'version': active_model.version if active_model else None,
            'input_size': self.model_input_size,
            'confidence_threshold': self.confidence_threshold,
            'class_names_loaded': bool(self.class_names),
            'metadata_keys': list(self.metadata.keys())
        }

    @staticmethod
    def delete_old_models(keep_latest=1):
        """Safe model cleanup with logging"""
        try:
            model_dir = os.path.join(settings.BASE_DIR, "models")
            if not os.path.exists(model_dir):
                return

            model_files = [f for f in os.listdir(model_dir) if f.endswith(('.h5', '.keras'))]
            model_files.sort(key=lambda f: os.path.getctime(os.path.join(model_dir, f)), reverse=True)

            for old_model in model_files[keep_latest:]:
                try:
                    os.remove(os.path.join(model_dir, old_model))
                    logger.info(f"Deleted old model: {old_model}")
                except Exception as e:
                    logger.error(f"Failed to delete {old_model}: {str(e)}")
        except Exception as e:
            logger.error(f"Model cleanup error: {str(e)}")
            raise