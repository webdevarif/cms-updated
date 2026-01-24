"""
URL configuration for translations API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'translations_v2'

router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'keys', views.TranslationKeyViewSet, basename='translation_key')
router.register(r'translations', views.TranslationViewSet, basename='translation')

urlpatterns = [
    path('', include(router.urls)),
]
