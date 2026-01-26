"""
Dashboard mediafile URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.MediafileDashboardViewSet, basename='dashboard-mediafiles')
router.register(r'folders', views.MediafolderDashboardViewSet, basename='dashboard-mediafolders')

urlpatterns = router.urls
