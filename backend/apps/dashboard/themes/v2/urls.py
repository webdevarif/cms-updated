"""
Dashboard themes URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'themes', views.ThemeDashboardViewSet, basename='dashboard-themes')
router.register(r'templates', views.TemplateDashboardViewSet, basename='dashboard-templates')

urlpatterns = router.urls
