"""
Dashboard test URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'test', views.TestDashboardViewSet, basename='dashboard-test')
router.register(r'test-deliveries', views.TestDeliveryDashboardViewSet, basename='dashboard-test-deliveries')

urlpatterns = router.urls
