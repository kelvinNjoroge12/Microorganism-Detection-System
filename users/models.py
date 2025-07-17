from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )

    is_admin = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )

    class Meta:
        app_label = 'users'  # Optional if Django detects the app correctly

    def __str__(self):
        return self.username  # ✅ Corrected

    def get_prediction_count(self):
        return self.prediction_set.count()


@receiver(post_save, sender=User)
def set_default_permissions(sender, instance, created, **kwargs):
    if created:
        if not instance.is_superuser:
            instance.is_staff = False
            instance.save()