"""
Public stores URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stores', views.StorePublicViewSet, basename='public-stores')

urlpatterns = router.urls
