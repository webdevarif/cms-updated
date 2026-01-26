"""
Dashboard test URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'test', views.TestDashboardViewSet, basename='dashboard-test')

urlpatterns = router.urls
