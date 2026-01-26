"""Customer posts API urls."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import CustomerPostViewSet, CommentCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r'posts', CustomerPostViewSet, basename='customer-post')
router.register(r'comments', CommentCustomerViewSet, basename='customer-comments')

urlpatterns = [
    path('', include(router.urls)),
]
