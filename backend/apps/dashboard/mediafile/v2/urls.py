"""
Dashboard mediafile URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'mediafile', views.MediafileDashboardViewSet, basename='dashboard-mediafile')

urlpatterns = router.urls
