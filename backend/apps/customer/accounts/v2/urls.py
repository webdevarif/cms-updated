"""
URL configuration for customer accounts API.

Customer-specific account management endpoints.
"""
from django.urls import path
from . import views

app_name = 'customer_accounts_v2'

urlpatterns = [
    # Profile management
    path('profile/', views.CustomerProfileView.as_view(), name='customer-profile'),
    path('profile/update/', views.CustomerProfileView.as_view(), name='customer-update-profile'),
    path('profile/delete/', views.CustomerDeleteAccountView.as_view(), name='customer-delete-account'),
    
    # Password management
    path('change-password/', views.CustomerChangePasswordView.as_view(), 
         name='customer-change-password'),
]
