from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    BlogViewSet,
    CategoryViewSet,
    CommentViewSet,
    PageViewSet,
    PolicyViewSet,
    PostMetaViewSet,
    PostTypeTemplateViewSet,
    PostTypeViewSet,
    PostViewSet,
    TagViewSet,
)

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r"post-types", PostTypeViewSet, basename="post-type")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"pages", PageViewSet, basename="page")
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"policy", PolicyViewSet, basename="policy")
router.register(r"post-meta", PostMetaViewSet, basename="post-meta")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"post-type-templates", PostTypeTemplateViewSet, basename="post-type-template")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]

# App name for namespacing
app_name = "posts"
