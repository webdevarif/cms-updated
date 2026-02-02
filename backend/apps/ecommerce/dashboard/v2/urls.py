"""
URL configuration for ecommerce dashboard API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartDashboardViewSet,
    CollectionDashboardViewSet,
    CouponCampaignDashboardViewSet,
    CouponDashboardViewSet,
    CustomerProfileDashboardViewSet,
    InventoryDashboardViewSet,
    OrderDashboardViewSet,
    PaymentDashboardViewSet,
    PaymentMethodDashboardViewSet,
    ProductCategoryDashboardViewSet,
    ProductDashboardViewSet,
    ProductVariantDashboardViewSet,
)

# Dashboard router
router = DefaultRouter()
router.register(r"products", ProductDashboardViewSet, basename="dashboard-products")
router.register(r"categories", ProductCategoryDashboardViewSet, basename="dashboard-categories")
router.register(r"variants", ProductVariantDashboardViewSet, basename="dashboard-variants")
router.register(r"inventory", InventoryDashboardViewSet, basename="dashboard-inventory")
router.register(r"carts", CartDashboardViewSet, basename="dashboard-carts")
router.register(r"collections", CollectionDashboardViewSet, basename="dashboard-collections")
router.register(r"orders", OrderDashboardViewSet, basename="dashboard-orders")
router.register(
    r"coupon-campaigns",
    CouponCampaignDashboardViewSet,
    basename="dashboard-coupon-campaigns",
)
router.register(r"coupons", CouponDashboardViewSet, basename="dashboard-coupons")
router.register(
    r"payment-methods",
    PaymentMethodDashboardViewSet,
    basename="dashboard-payment-methods",
)
router.register(r"payments", PaymentDashboardViewSet, basename="dashboard-payments")
router.register(
    r"customer-profiles",
    CustomerProfileDashboardViewSet,
    basename="dashboard-customer-profiles",
)

urlpatterns = [
    path("", include(router.urls)),
]
