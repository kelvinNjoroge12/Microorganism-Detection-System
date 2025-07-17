from django.apps import AppConfig

class PredictionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictions'

    def ready(self):
        # Try to load model at startup
        from .model_service import AIClassifier
        classifier = AIClassifier()
        if not classifier.load_model():
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Failed to load model during app initialization")