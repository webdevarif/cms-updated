"""
URL configuration for logs API v2.
"""
from django.urls import path
from . import views

app_name = 'logs_v2'

urlpatterns = [
    path('', views.LogEntryViewSet.as_view({'get': 'list'}), name='log-list'),
    path('<int:pk>/', views.LogEntryViewSet.as_view({'get': 'retrieve'}), name='log-detail'),
    path('analytics/', views.StoreAnalyticsView.as_view({'get': 'list'}), name='store-analytics'),
    path('security/', views.SecurityEventsView.as_view({'get': 'list'}), name='security-events'),
    path('track-event/', views.track_event, name='track-event'),
]
