from django.conf import settings

def site_settings(request):
    return {
        'SITE_NAME': 'Food Safety Analyzer',
        'DEBUG': settings.DEBUG,
    }