#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core1.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH? Did you forget to activate "
            "a virtual environment?"
        ) from exc
    except Exception as e:
        print(f"Error during Django initialization: {str(e)}")
        sys.exit(1)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

from predictions.models import ModelVersion

active_model = ModelVersion.objects.filter(is_active=True).first()
if active_model:
    print(f"Active model: {active_model.version}")
    print(f"Model file exists: {active_model.model_file.path if active_model.model_file else 'None'}")
    if active_model.model_file:
        print(f"File size: {active_model.model_file.size} bytes")
else:
    print("No active model found")
from predictions.model_service import AIClassifier

classifier = AIClassifier()
if classifier.load_model():
    print("✅ Model loaded successfully!")
    print(f"Model version: {classifier.current_model_version}")
    print(f"Input size: {classifier.model_input_size}")
    print(f"Class names: {classifier.class_names}")
else:
    print("❌ Failed to load model")