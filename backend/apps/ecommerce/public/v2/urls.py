"""
URL configuration for ecommerce public API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    CartPublicViewSet,
    CollectionPublicViewSet,
    CustomerProfilePublicViewSet,
    ProductCategoryPublicViewSet,
    ProductPublicViewSet,
    ReviewPublicViewSet,
)

# Public router
router = DefaultRouter()
router.register(r"products", ProductPublicViewSet, basename="public-products")
router.register(r"categories", ProductCategoryPublicViewSet, basename="public-categories")
router.register(r"carts", CartPublicViewSet, basename="public-carts")
router.register(r"collections", CollectionPublicViewSet, basename="public-collections")
router.register(
    r"customer-profiles", CustomerProfilePublicViewSet, basename="public-customer-profiles"
)

# Nested router for reviews under products
products_router = routers.NestedDefaultRouter(router, r"products", lookup="product")
products_router.register(r"reviews", ReviewPublicViewSet, basename="public-reviews")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
]
