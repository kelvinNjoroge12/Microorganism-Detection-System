# predictions/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Prediction  # Changed from Predictions to Prediction

User = get_user_model()

@receiver(post_save, sender=Prediction)  # Changed to Prediction
def update_user_prediction_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.save()  # This will update any denormalized counts