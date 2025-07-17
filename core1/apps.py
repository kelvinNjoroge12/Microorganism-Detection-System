from django.apps import AppConfig

class Core1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core1'
    verbose_name = "Main Application"

    def ready(self):
        # Import signals
        import core1.signals  # noqa


from django.apps import AppConfig

class PredictionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictions'

    def ready(self):
        # Import signals and template tags
        import predictions.signals  # if you have signals
        import predictions.templatetags.custom_filters  # noqa: F401