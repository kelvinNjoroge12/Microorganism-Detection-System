import logging
from django.http import JsonResponse
from django.conf import settings
import whitenoise
whitenoise.middleware.WhiteNoiseMiddleware

logger = logging.getLogger(__name__)

class ModelHealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/healthcheck/':
            from predictions.model_service import get_classifier
            classifier = get_classifier()
            return JsonResponse({
                'model_loaded': classifier is not None and hasattr(classifier, 'model'),
                'status': 'ok' if classifier and classifier.model else 'error'
            })
        return self.get_response(request)
