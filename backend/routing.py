"""
WebSocket routing for Django Channels.
Routes WebSocket connections to appropriate consumers.
"""
from django.urls import path
from consumers import (
    NotificationsConsumer,
    SearchConsumer,
    DashboardConsumer
)

websocket_urlpatterns = [
    # Notifications WebSocket
    path('ws/notifications/', NotificationsConsumer.as_asgi()),

    # Search WebSocket
    path('ws/search/', SearchConsumer.as_asgi()),

    # Dashboard WebSocket
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
]
