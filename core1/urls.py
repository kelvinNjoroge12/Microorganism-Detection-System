from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core1 import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),

    # Include other apps' URLs correctly
    path('predictions/', include('predictions.urls', namespace='predictions')),
    path('users/', include('users.urls', namespace='users')),

    # Authentication paths
    path('accounts/', include('django.contrib.auth.urls')),

    # Other views from core1/views.py
    path('upload/', views.upload_images, name='upload_images'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/', views.profile, name='profile'),
]

# Serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
