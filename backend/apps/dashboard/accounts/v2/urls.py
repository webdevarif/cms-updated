"""
URL configuration for dashboard accounts API.

Dashboard-specific user management endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
try:
    from rest_framework_nested import routers
except ImportError:
    routers = None
from . import views, permission_views, activity_views

app_name = 'dashboard_accounts_v2'

router = DefaultRouter()
router.register(r'users', views.StoreUserViewSet, basename='store-user')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'permissions', permission_views.PermissionViewSet, basename='permission')

# Nested routes for user activity
if routers:
    users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
    users_router.register(r'activity', activity_views.UserActivityViewSet, basename='user-activity')
else:
    users_router = None

urlpatterns = [
    path('', include(router.urls)),
]
if users_router:
    urlpatterns.append(path('', include(users_router.urls)))
