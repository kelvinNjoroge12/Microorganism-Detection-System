from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password/change/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/change_password.html',
             success_url='/users/profile/'
         ),
         name='password_change'),
    path('predictions/', views.user_predictions, name='user_predictions')
]