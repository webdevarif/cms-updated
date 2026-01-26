"""
Customer SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'smtp', views.SmtpCustomerViewSet, basename='customer-smtp')

urlpatterns = router.urls
