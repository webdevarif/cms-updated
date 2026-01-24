"""
URL configuration for Digital Farmers CMS accounts API.

Public and authenticated account endpoints.
"""
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    ProfileView,
)

app_name = 'accounts'

urlpatterns = [
    # Public endpoints (no authentication)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # Authenticated endpoints
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
