"""
URL configuration for gift cards API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'giftcards_v2'

router = DefaultRouter()
router.register(r'gift-cards', views.GiftCardViewSet, basename='gift_card')
router.register(r'gift-card-history', views.GiftCardHistoryViewSet, basename='gift_card_history')

urlpatterns = [
    path('', include(router.urls)),
]
