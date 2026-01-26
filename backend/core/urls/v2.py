"""
API v2 URL configuration for Digital Farmers CMS.
"""
from django.urls import path, include
from django.contrib import admin

app_name = 'v2'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
]
