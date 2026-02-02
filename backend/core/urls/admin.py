"""
Admin URL configuration for Digital Farmers CMS.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
