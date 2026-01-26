"""
Dashboard SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'smtp', views.SmtpDashboardViewSet, basename='dashboard-smtp')

urlpatterns = router.urls
