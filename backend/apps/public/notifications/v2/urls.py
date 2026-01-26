"""
Public notifications URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationPublicViewSet, basename='public-notifications')

urlpatterns = router.urls
