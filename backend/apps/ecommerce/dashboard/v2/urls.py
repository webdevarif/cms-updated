"""
URL configuration for ecommerce dashboard API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartDashboardViewSet,
    CouponCampaignDashboardViewSet,
    CouponDashboardViewSet,
    CustomerProfileDashboardViewSet,
    DashboardCollectionViewSet,
    DashboardInventoryViewSet,
    DashboardProductViewSet,
    OrderDashboardViewSet,
    OrderItemDashboardViewSet,
    PaymentDashboardViewSet,
    PaymentMethodDashboardViewSet,
    ProductCategoryDashboardViewSet,
    ProductVariantDashboardViewSet,
    ReviewDashboardViewSet,
)

# Dashboard router
router = DefaultRouter()
router.register(r"products", DashboardProductViewSet, basename="dashboard-products")
router.register(r"categories", ProductCategoryDashboardViewSet, basename="dashboard-categories")
router.register(r"variants", ProductVariantDashboardViewSet, basename="dashboard-variants")
router.register(r"inventory", DashboardInventoryViewSet, basename="dashboard-inventory")
router.register(r"carts", CartDashboardViewSet, basename="dashboard-carts")
router.register(r"collections", DashboardCollectionViewSet, basename="dashboard-collections")
router.register(r"orders", OrderDashboardViewSet, basename="dashboard-orders")
router.register(r"order-items", OrderItemDashboardViewSet, basename="dashboard-order-items")
router.register(
    r"coupon-campaigns", CouponCampaignDashboardViewSet, basename="dashboard-coupon-campaigns"
)
router.register(r"coupons", CouponDashboardViewSet, basename="dashboard-coupons")
router.register(
    r"payment-methods", PaymentMethodDashboardViewSet, basename="dashboard-payment-methods"
)
router.register(r"payments", PaymentDashboardViewSet, basename="dashboard-payments")
router.register(
    r"customer-profiles", CustomerProfileDashboardViewSet, basename="dashboard-customer-profiles"
)
router.register(r"reviews", ReviewDashboardViewSet, basename="dashboard-reviews")

urlpatterns = [
    path("", include(router.urls)),
]
