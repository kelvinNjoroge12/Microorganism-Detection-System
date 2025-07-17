import os
import sys
from io import BytesIO
from PIL import Image


def setup_django():
    """Configure Django environment for standalone scripts"""
    import django
    from django.conf import settings

    # Set up Django environment
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_path)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core1.settings')  # Replace 'core1' with your project name
    django.setup()


def test_classifier_with_local_image():
    # First setup Django environment
    setup_django()

    # Now import your classifier after Django is configured
    from predictions.model_service import AIClassifier

    # Initialize the classifier
    classifier = AIClassifier()

    if not classifier.load_model():
        print("❌ Failed to load model")
        return

    # Test with a local image
    image_path = r"C:\Users\Admin\core1\static\images\bg2.png"

    try:
        # Load image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Make prediction
        result = classifier.predict(image_bytes)

        if result['success']:
            print("\n✅ Prediction successful!")
            print(f"Microorganism: {result['microorganism']}")
            print(f"Full Name: {result['full_name']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Is Harmful: {result['is_harmful']}")
            print(f"Food Source: {result['food_source']}")
        else:
            print("\n❌ Prediction failed:")
            print(f"Error: {result['error']}")
            if 'confidence' in result:
                print(f"Confidence: {result['confidence']:.2%}")

    except FileNotFoundError:
        print(f"\n❌ Image file not found at: {image_path}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")


if __name__ == "__main__":
    print("Starting classifier test...")
    test_classifier_with_local_image()