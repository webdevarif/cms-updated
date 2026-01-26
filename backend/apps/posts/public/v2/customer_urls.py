"""Customer posts API urls."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerPostViewSet

router = DefaultRouter()
router.register(r'posts', CustomerPostViewSet, basename='customer-post')

urlpatterns = [
    path('v2/api/customer/posts/', include(router.urls)),
]
