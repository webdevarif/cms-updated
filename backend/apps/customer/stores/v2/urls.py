"""
Customer stores URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stores', views.StoreCustomerViewSet, basename='customer-stores')

urlpatterns = router.urls
