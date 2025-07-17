from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class ModelVersion(models.Model):
    version = models.CharField(max_length=50, unique=True)
    model_file = models.FileField(
        upload_to='models/',
        validators=[FileExtensionValidator(allowed_extensions=['h5', 'keras'])]
    )
    encoder_file = models.FileField(
        upload_to='encoders/',
        validators=[FileExtensionValidator(allowed_extensions=['pkl'])],
        null=True,
        blank=True,
        help_text="Label encoder file (.pkl)"
    )
    release_notes = models.TextField()
    accuracy = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Model accuracy score between 0 and 1"
    )
    is_active = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Model Version"
        verbose_name_plural = "Model Versions"

    def __str__(self):
        return f"Model v{self.version} - {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        if self.is_active:
            ModelVersion.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.model_file:
            self.model_file.delete(save=False)
        if self.encoder_file:
            self.encoder_file.delete(save=False)
        super().delete(*args, **kwargs)

class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'predictions'
    )
    image = models.ImageField(upload_to='predictions/%Y/%m/%d/')
    microorganism = models.CharField(max_length=100)
    harmful = models.BooleanField()
    food_source = models.CharField(max_length=200)
    confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    model_version = models.CharField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_predictions'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    model_version = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['user', 'date_created']),
            models.Index(fields=['microorganism']),
            models.Index(fields=['harmful']),
            models.Index(fields=['confidence']),
            models.Index(fields=['food_source']),
        ]

    def __str__(self):
        return f"{self.microorganism} ({self.confidence:.2%}) - {self.user.get_username()}"

    def get_status_display(self):
        return "Harmful" if self.harmful else "Safe"

    def verify(self, user, notes=""):
        self.verified_by = user
        self.verification_date = timezone.now()
        self.verification_notes = notes
        self.save()