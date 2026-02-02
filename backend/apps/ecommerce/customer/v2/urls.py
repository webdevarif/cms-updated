"""
URL configuration for ecommerce customer API v2.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartCustomerViewSet,
    CollectionCustomerViewSet,
    CouponCustomerViewSet,
    CustomerProfileCustomerViewSet,
    OrderCustomerViewSet,
    PaymentCustomerViewSet,
    PaymentMethodCustomerViewSet,
    ProductCategoryCustomerViewSet,
    ProductCustomerViewSet,
)

# Customer router
router = DefaultRouter()
router.register(r"products", ProductCustomerViewSet, basename="customer-products")
router.register(r"categories", ProductCategoryCustomerViewSet, basename="customer-categories")
router.register(r"carts", CartCustomerViewSet, basename="customer-carts")
router.register(r"collections", CollectionCustomerViewSet, basename="customer-collections")
router.register(
    r"customer-profiles",
    CustomerProfileCustomerViewSet,
    basename="customer-customer-profiles",
)
router.register(r"orders", OrderCustomerViewSet, basename="customer-orders")
router.register(r"coupons", CouponCustomerViewSet, basename="customer-coupons")
router.register(
    r"payment-methods",
    PaymentMethodCustomerViewSet,
    basename="customer-payment-methods",
)
router.register(r"payments", PaymentCustomerViewSet, basename="customer-payments")

urlpatterns = [
    path("", include(router.urls)),
]
