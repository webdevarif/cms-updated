"""
Customer notifications URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationCustomerViewSet, basename='customer-notifications')
router.register(r'preferences', views.NotificationPreferenceCustomerViewSet, basename='customer-notification-preferences')

urlpatterns = router.urls
