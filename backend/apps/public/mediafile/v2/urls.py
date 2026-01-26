"""
Public mediafile URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.MediafilePublicViewSet, basename='public-mediafiles')
router.register(r'folders', views.MediafolderPublicViewSet, basename='public-mediafolders')

urlpatterns = router.urls
