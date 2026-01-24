"""
URL configuration for public accounts API.

Public authentication endpoints for registration, login, and logout.
"""
from django.urls import path
from . import views

app_name = 'public_accounts_v2'

urlpatterns = [
    # Public endpoints (no authentication)
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('verify-email/', views.EmailVerificationView.as_view(), name='verify-email'),
]
