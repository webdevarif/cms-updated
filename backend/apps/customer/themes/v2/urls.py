"""
Customer themes URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'themes', views.ThemeCustomerViewSet, basename='customer-themes')

urlpatterns = router.urls
