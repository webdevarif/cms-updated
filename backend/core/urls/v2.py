"""
API v2 URL configuration for Digital Farmers CMS.
"""
from django.contrib import admin
from django.urls import include, path

app_name = "v2"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
]
