"""
Public themes URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'themes', views.ThemePublicViewSet, basename='public-themes')

urlpatterns = router.urls
