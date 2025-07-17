from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django.core.signals import request_finished
from django.dispatch import receiver
import imghdr
import logging

from django.views.decorators.http import require_POST

from .forms import ImageUploadForm, ModelUploadForm, ModelUpdateForm
from .models import Prediction, ModelVersion
from .model_service import AIClassifier

logger = logging.getLogger(__name__)

# Global classifier instance managed through a function
_classifier_instance = None


def get_classifier():
    """Singleton pattern to manage classifier instance with proper initialization"""
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = AIClassifier()
        try:
            if not _classifier_instance.load_model():
                logger.error("Failed to load model during classifier initialization")
                # Don't return None, return the instance even if model failed to load
        except Exception as e:
            logger.error(f"Classifier initialization failed: {str(e)}", exc_info=True)
            _classifier_instance = AIClassifier()  # Still return an instance

    return _classifier_instance


def parse_prediction_data(full_name):
    """
    Parses the full microorganism name into components.
    Expected format: "Spherical_bacteria_1_Contaminated dairy products, raw meat"
    Returns:
        - display_name: "Spherical bacteria"
        - scientific_name: "Spherical_bacteria"
        - harmful: True/False
        - food_sources: ["dairy products", "raw meat"]
    """
    if not full_name:
        return "", "", False, []

    parts = full_name.split('_')

    # Basic components
    microorganism_name = parts[0]
    scientific_name = microorganism_name

    # Check if the microorganism name has multiple words
    if '_' in microorganism_name:
        display_name = microorganism_name.replace('_', ' ').title()
    else:
        display_name = microorganism_name.title()

    # Harmful status (1 = harmful, 0 = safe)
    harmful = len(parts) > 1 and parts[1] == "1"

    # Food sources (everything after the status)
    food_sources = []
    if len(parts) > 2:
        food_str = '_'.join(parts[2:])
        # Split by commas if present, otherwise use whole string
        if ',' in food_str:
            food_sources = [s.strip() for s in food_str.split(',') if s.strip()]
        else:
            food_sources = [food_str]

    return display_name, scientific_name, harmful, food_sources


@login_required
def upload_images(request):
    classifier = get_classifier()
    if not classifier.model and not classifier.load_model():
        messages.error(request, "Model failed to load. Please contact administrator.")
        return redirect('home')

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            batch_predictions = []
            successful_uploads = 0
            failed_predictions = []  # Store failed predictions

            for image in request.FILES.getlist('images'):
                try:
                    if not imghdr.what(image):
                        messages.error(request, f"Invalid image format: {image.name}")
                        continue

                    image_bytes = image.read()
                    result = classifier.predict(image_bytes)

                    if not result.get('success'):
                        msg = f"Classification failed for {image.name}: {result.get('error', 'Unknown error')}"
                        messages.warning(request, msg)
                        logger.warning(msg)
                        continue

                    # Parse the prediction result
                    display_name, scientific_name, harmful, food_sources = parse_prediction_data(result['full_name'])
                    food_source_str = ", ".join(food_sources) if food_sources else "Unknown"

                    prediction = Prediction(
                        user=request.user,
                        image=image,
                        microorganism=scientific_name,
                        harmful=harmful,
                        food_source=food_source_str,
                        confidence=result['confidence'],
                        model_version=classifier.current_model_version
                    )
                    prediction.save()
                    successful_uploads += 1
                    batch_predictions.append(prediction.id)

                    try:
                        send_prediction_notification(
                            request.user.email,
                            display_name,
                            result['confidence'],
                            harmful
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send notification email: {str(e)}")

                except Exception as e:
                    error_msg = f"Error processing {image.name}: {str(e)}"
                    messages.error(request, error_msg)
                    logger.error(error_msg, exc_info=True)
                    continue

            if successful_uploads > 0:
                # Store batch prediction IDs in session
                request.session[f'batch_upload_{request.user.id}'] = batch_predictions
                if failed_predictions:
                    request.session['failed_predictions'] = failed_predictions

                if successful_uploads == 1:
                    return redirect('predictions:analysis_result', prediction_id=batch_predictions[0])
                else:
                    messages.success(request, f"Successfully processed {successful_uploads} images")
                    return redirect('predictions:prediction_history')
            else:
                messages.error(request, "No images were successfully processed")
                return redirect('predictions:upload_images')
    else:
        form = ImageUploadForm()

    return render(request, 'predictions/upload_images.html', {
        'form': form,
        'model_version': classifier.current_model_version,
        'model_loaded': classifier.model is not None
    })

@login_required
def analyze_result(request, prediction_id):
    # Get the main prediction being viewed
    prediction = get_object_or_404(Prediction, id=prediction_id, user=request.user)

    # Get the session key where we stored the batch upload IDs
    batch_ids = request.session.get(f'batch_upload_{request.user.id}', [])

    # Get all predictions from this batch (including current one)
    batch_predictions = Prediction.objects.filter(
        id__in=batch_ids,
        user=request.user
    ).order_by('-date_created')[:10]  # Limit to 10

    # Get recent predictions (excluding current batch)
    recent_predictions = Prediction.objects.filter(
        user=request.user
    ).exclude(id__in=batch_ids).order_by('-date_created')[:10]

    # Parse the current prediction data
    display_name, scientific_name, harmful, food_sources = parse_prediction_data(prediction.microorganism)

    context = {
        'prediction': prediction,
        'display_name': display_name,
        'scientific_name': scientific_name,
        'harmful': harmful,
        'food_sources': food_sources,
        'confidence_percent': f"{prediction.confidence * 100:.1f}%",
        'model_version': prediction.model_version,
        'model_status': "Active" if ModelVersion.objects.filter(is_active=True).exists() else "Inactive",
        'batch_predictions': batch_predictions,  # All predictions from this upload batch
        'recent_predictions': recent_predictions  # Other recent predictions
    }
    return render(request, 'predictions/result.html', context)

@login_required
def prediction_history(request):
    predictions = Prediction.objects.filter(user=request.user).select_related('user').order_by('-date_created')

    food_source = request.GET.get('food_source')
    if food_source:
        predictions = predictions.filter(food_source__icontains=food_source)

    harmful_filter = request.GET.get('harmful')
    if harmful_filter in ['true', 'false']:
        predictions = predictions.filter(harmful=(harmful_filter == 'true'))

    paginator = Paginator(predictions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'predictions/prediction_history.html', {
        'page_obj': page_obj,
        'food_sources': Prediction.objects.filter(user=request.user)
                  .values_list('food_source', flat=True)
                  .distinct(),
        'selected_source': food_source,
        'harmful_filter': harmful_filter
    })


@login_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk, user=request.user)

    # Parse the stored data
    display_name, scientific_name, harmful, food_sources = parse_prediction_data(prediction.microorganism)

    return render(request, 'predictions/prediction_detail.html', {
        'prediction': prediction,
        'display_name': display_name,
        'scientific_name': scientific_name,
        'harmful': harmful,
        'food_sources': food_sources,
        'confidence_percent': f"{prediction.confidence * 100:.1f}%",
        'model_version': prediction.model_version
    })


# Model management views (remain unchanged)
@user_passes_test(lambda u: u.is_superuser)
def model_upload(request):
    classifier = get_classifier()
    if request.method == 'POST':
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                model_version = form.save(commit=False)
                model_version.uploaded_by = request.user
                model_version.save()
                if not classifier.load_model():
                    messages.error(request, "Model uploaded but failed to load!")
                else:
                    messages.success(request, f"Model '{model_version.version}' uploaded and loaded successfully!")
                return redirect('predictions:update_model')
            except Exception as e:
                messages.error(request, f"Error saving model: {str(e)}")
                logger.error(f"Model upload failed: {str(e)}", exc_info=True)
    else:
        form = ModelUploadForm()

    return render(request, 'predictions/model_upload.html', {
        'form': form,
        'active_tab': 'upload',
        'model_status': classifier.get_status()
    })


@user_passes_test(lambda u: u.is_superuser)
def activate_model(request, pk):
    classifier = get_classifier()
    try:
        ModelVersion.objects.exclude(pk=pk).update(is_active=False)
        model = ModelVersion.objects.get(pk=pk)
        model.is_active = True
        model.save()
        if classifier.load_model():
            messages.success(request, f"Model '{model.version}' activated and loaded successfully!")
        else:
            messages.error(request, f"Model '{model.version}' activated but failed to load!")
    except Exception as e:
        messages.error(request, f"Error activating model: {str(e)}")
        logger.error(f"Model activation failed: {str(e)}", exc_info=True)
    return redirect('predictions:update_model')


@user_passes_test(lambda u: u.is_superuser)
def update_model(request):
    classifier = get_classifier()
    classifier.load_model()
    return render(request, 'predictions/update_model.html', {
        'active_model': ModelVersion.objects.filter(is_active=True).first(),
        'all_models': ModelVersion.objects.all().order_by('-uploaded_at'),
        'active_tab': 'update',
        'model_status': classifier.get_status()
    })


@user_passes_test(lambda u: u.is_superuser)
def delete_model(request, pk):
    classifier = get_classifier()
    model = get_object_or_404(ModelVersion, pk=pk)
    if request.method == 'POST':
        try:
            version = model.version
            was_active = model.is_active
            model.model_file.delete(save=False)
            model.encoder_file.delete(save=False)
            model.delete()
            messages.success(request, f"Model v{version} deleted successfully!")
            if was_active and not classifier.load_model():
                messages.warning(request, "Active model was deleted but failed to load replacement")
            return redirect('predictions:update_model')
        except Exception as e:
            messages.error(request, f"Error deleting model: {str(e)}")
            logger.error(f"Failed to delete model {pk}: {str(e)}", exc_info=True)
    return render(request, 'predictions/model_confirm_delete.html', {
        'model': model,
        'active_tab': 'update',
        'is_active_model': model.is_active
    })


def cleanup_classifier():
    global _classifier_instance
    _classifier_instance = None


@receiver(request_finished)
def clean_up(sender, **kwargs):
    cleanup_classifier()


def send_prediction_notification(user_email, microorganism, confidence, is_harmful):
    subject = "New Prediction Result"
    harmful_status = "Harmful" if is_harmful else "Safe"
    message = f"""Hello,

Your recent food prediction detected '{microorganism}' with a confidence of {confidence:.2f}%.
Status: {harmful_status}.

Thank you!"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

@require_POST
def clear_failed_predictions(request):
    if 'failed_predictions' in request.session:
        del request.session['failed_predictions']
    return JsonResponse({'status': 'success'})
def health_check(request):
    classifier = get_classifier()
    return JsonResponse({
        'status': 'ok' if classifier and hasattr(classifier, 'model') and classifier.model else 'error',
        'model_loaded': classifier.model is not None if classifier else False,
        'model_version': classifier.current_model_version if classifier else None
    })