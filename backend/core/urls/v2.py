"""
API v2 URL configuration for Digital Farmers CMS.
"""
from django.contrib import admin
from django.urls import include, path

from ..views import api_root

app_name = "v2"

urlpatterns = [
    # API Root
    path("", api_root, name="api_root"),
    # Admin
    path("admin/", admin.site.urls),
]
