from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import path

from users import views


def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    if request.method == 'POST':
        # Process contact form submission
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # Redirect to avoid resubmission on refresh
    return render(request, "contact.html")

def login_view(request):
    return render(request, "users/login.html")

def register(request):
    return render(request, 'users/register.html')

@login_required
def upload_images(request):
    return render(request, 'predictions/upload_images.html')

@login_required
def prediction_history(request):
    return render(request, 'predictions/prediction_history.html')

@login_required
def profile_update(request):
    return render(request, 'users/profile_update.html')

@login_required
def profile(request):
    return render(request, 'users/profile.html')



