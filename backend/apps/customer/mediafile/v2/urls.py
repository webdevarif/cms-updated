"""
Customer mediafile URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'mediafile', views.MediafileCustomerViewSet, basename='customer-mediafile')

urlpatterns = router.urls
