"""
Public webhooks URL configuration.
"""
from django.urls import path

from . import views

urlpatterns = [
    path("webhooks/<uuid:webhook_id>", views.WebhookPublicView.as_view(), name="webhook-delivery"),
    path(
        "webhooks/status/<uuid:webhook_id>/",
        views.WebhookStatusView.as_view(),
        name="webhook-status",
    ),
    path("webhooks/status/", views.WebhookStatusView.as_view(), name="webhook-status-list"),
]
