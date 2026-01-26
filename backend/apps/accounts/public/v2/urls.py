"""
URL configuration for accounts public API v2.
"""
from django.urls import path

from .views import (
    PublicLoginView,
    PublicRegistrationView,
    ForgotPasswordView,
    ResetPasswordView
)

urlpatterns = [
    path('login/', PublicLoginView.as_view(), name='login'),
    path('register/', PublicRegistrationView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
