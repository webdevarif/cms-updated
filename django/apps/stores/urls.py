from apps.themes.views import (
    ColorSchemeViewSet,
    LayoutViewSet,
    StyleClassViewSet,
    TemplateViewSet,
    ThemeViewSet,
)
from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    StoreAPIKeyViewSet,
    StoreMembershipViewSet,
    StoreRoleViewSet,
    StoreUserRoleViewSet,
    StoreViewSet,
)

# Main stores router
router = DefaultRouter()
router.register(r"", StoreViewSet, basename="store")
router.register(r"memberships", StoreMembershipViewSet, basename="store-membership")

# Store-specific router for nested resources
store_router = DefaultRouter()
store_router.register(r"roles", StoreRoleViewSet, basename="store-role")
store_router.register(r"user-roles", StoreUserRoleViewSet, basename="store-user-role")
store_router.register(r"api-keys", StoreAPIKeyViewSet, basename="store-api-key")
store_router.register(r"themes", ThemeViewSet, basename="store-theme")
store_router.register(r"color-schemes", ColorSchemeViewSet, basename="store-color-scheme")
store_router.register(r"layouts", LayoutViewSet, basename="store-layout")
store_router.register(r"style-classes", StyleClassViewSet, basename="store-style-class")
store_router.register(r"templates", TemplateViewSet, basename="store-template")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:store_pk>/", include(store_router.urls)),
]
