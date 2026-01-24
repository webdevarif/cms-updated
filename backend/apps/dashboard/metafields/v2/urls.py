from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'definitions', views.MetafieldDefinitionViewSet, basename='metafield-definition')
router.register(r'values', views.MetafieldViewSet, basename='metafield')

urlpatterns = [
    path('', include(router.urls)),
]
