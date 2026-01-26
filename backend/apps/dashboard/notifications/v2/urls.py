"""
Dashboard notifications URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationDashboardViewSet, basename='dashboard-notifications')
router.register(r'preferences', views.NotificationPreferenceDashboardViewSet, basename='dashboard-notification-preferences')

urlpatterns = router.urls
