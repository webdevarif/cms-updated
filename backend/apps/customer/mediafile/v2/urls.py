"""
Customer mediafile URL configuration.
"""
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.MediafileCustomerViewSet, basename='customer-mediafiles')
router.register(r'folders', views.MediafolderCustomerViewSet, basename='customer-mediafolders')

urlpatterns = router.urls
