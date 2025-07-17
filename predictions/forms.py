from django import forms
from django.core.validators import FileExtensionValidator
from .models import ModelVersion

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            if len(data) > 10:
                raise forms.ValidationError("You can only upload up to 10 images at a time.")
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ImageUploadForm(forms.Form):
    images = MultipleFileField(
        label='Upload Images (Max 10)',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

class ModelUploadForm(forms.ModelForm):
    class Meta:
        model = ModelVersion
        fields = ['version', 'model_file', 'encoder_file', 'release_notes', 'accuracy']
        widgets = {
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'model_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.h5,.keras'
            }),
            'encoder_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pkl'
            }),
            'release_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'accuracy': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1'
            })
        }

class ModelUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelVersion
        fields = ['version', 'model_file', 'encoder_file', 'release_notes', 'accuracy', 'is_active']
        widgets = {
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'model_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.h5,.keras'
            }),
            'encoder_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pkl'
            }),
            'release_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'accuracy': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }