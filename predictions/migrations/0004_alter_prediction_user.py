# Generated by Django 4.2 on 2025-04-03 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0003_modelversion_encoder_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to=settings.AUTH_USER_MODEL),
        ),
    ]
