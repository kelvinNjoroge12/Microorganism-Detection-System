# predictions/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from predictions.models import Prediction  # Use full path

User = get_user_model()

@receiver(post_save, sender=Prediction)
def update_user_prediction_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.save()