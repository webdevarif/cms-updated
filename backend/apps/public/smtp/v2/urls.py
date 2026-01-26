"""
Public SMTP URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'smtp', views.SmtpPublicViewSet, basename='public-smtp')

urlpatterns = router.urls
