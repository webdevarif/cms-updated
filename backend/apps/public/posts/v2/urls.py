"""Public posts API urls."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicPostViewSet

router = DefaultRouter()
router.register(r'posts', PublicPostViewSet, basename='public-post')

urlpatterns = [
    path('v2/api/public/posts/', include(router.urls)),
]
