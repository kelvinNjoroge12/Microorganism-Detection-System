from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    # Image prediction endpoints
    path('upload/', views.upload_images, name='upload_images'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('history/<int:pk>/', views.prediction_detail, name='prediction_detail'),
    path('result/<int:prediction_id>/', views.analyze_result, name='analysis_result'),
    path('clear-failed-predictions/', views.clear_failed_predictions, name='clear_failed_predictions'),
    path('health/', views.health_check, name='health_check'),
    # Model management endpoints
    path('model/upload/', views.model_upload, name='model_upload'),
    path('model/update/', views.update_model, name='update_model'),

    # Admin actions
    path('model/activate/<int:pk>/', views.activate_model, name='activate_model'),
    path('model/delete/<int:pk>/', views.delete_model, name='delete_model'),


]
