"""
URL configuration for queue API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'queue_v2'

router = DefaultRouter()
router.register(r'tasks', views.QueueTaskViewSet, basename='queue_task')

urlpatterns = [
    path('', include(router.urls)),
]
