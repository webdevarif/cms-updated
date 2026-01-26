"""
Dashboard stores URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stores', views.StoreDashboardViewSet, basename='dashboard-stores')

urlpatterns = router.urls
