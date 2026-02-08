from apps.accounts.permissions import HasStoreAccess
from apps.stores.utils import StoreScopedMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models import Count, Q

from .models import Category, Comment, Post, PostMeta, PostType, Tag
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    PageSerializer,
    PostCreateSerializer,
    PostMetaSerializer,
    PostSerializer,
    PostTypeSerializer,
    PostTypeTemplateSerializer,
    TagSerializer,
)
from .services import create_builtin_post_types_for_store, get_published_posts


class PostTypeViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing post types.
    """

    serializer_class = PostTypeSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "is_active",
        "is_builtin",
    ]  # Removed 'store' as we'll handle it in get_queryset
    search_fields = ["name", "key", "description"]
    ordering_fields = ["name", "key", "created_at", "updated_at"]
    ordering = ["-is_builtin", "name"]

    def get_queryset(self):
        """
        Filter post types by store.
        """
        return PostType.objects.filter(store=self.store)

    def perform_create(self, serializer):
        """
        Create post type for the specified store.
        """
        serializer.save(store=self.store)

    def perform_destroy(self, instance):
        """
        Prevent deletion of builtin post types.
        """
        if instance.is_builtin:
            return Response(
                {"error": "Cannot delete builtin post types"}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def create_builtin(self, request, pk=None):
        """
        Create builtin post types for a store.
        """
        post_type = self.get_object()
        builtins = create_builtin_post_types_for_store(post_type.store)
        serializer = self.get_serializer(builtins.values(), many=True)
        return Response(serializer.data)


class PostViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing posts.
    """

    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "post_type",
        "status",
        "is_featured",
        "content_type",
    ]  # Removed 'store' as we filter in get_queryset
    search_fields = ["title", "slug", "excerpt", "content"]
    ordering_fields = ["title", "slug", "created_at", "updated_at", "published_at"]
    ordering = ["-published_at", "-created_at"]

    def get_serializer_class(self):
        """
        Use PostCreateSerializer for creation, PostSerializer for other operations.
        """
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        """
        Filter posts by store.
        """
        return Post.objects.select_related("post_type", "store").filter(store=self.store)

    def perform_create(self, serializer):
        """
        Create post with proper store scoping. Set default post_type if not provided.
        """
        # If post_type not specified, find or create the 'post' post type
        if "post_type" not in serializer.validated_data:
            try:
                post_type = PostType.objects.get(store=self.store, key="post")
                serializer.validated_data["post_type"] = post_type
            except PostType.DoesNotExist:
                return Response(
                    {"error": "Post post type not found for this store"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update post with user tracking.
        """
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=["get"])
    def published(self, request):
        """
        Get published posts only.
        """
        store_id = request.query_params.get("store")
        post_type_key = request.query_params.get("post_type_key")

        if not store_id:
            return Response(
                {"error": "store parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        posts = get_published_posts(
            store_id=store_id, post_type_key=post_type_key, filters=request.query_params.dict()
        )

        # Remove service-specific params from filters
        exclude_params = ["store", "post_type_key"]
        filters = {k: v for k, v in request.query_params.items() if k not in exclude_params}

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post", "put", "delete"])
    def meta(self, request, pk=None):
        """
        Manage metadata for a specific post.
        """
        post = self.get_object()

        if request.method == "GET":
            meta = post.meta.all()
            serializer = PostMetaSerializer(meta, many=True)
            return Response(serializer.data)

        elif request.method in ["POST", "PUT"]:
            serializer = PostMetaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            key = request.data.get("key")
            if key:
                post.meta.filter(key=key).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "key parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )


class PageViewSet(PostViewSet):
    """
    ViewSet for managing pages (posts with post_type.key='page').
    """

    serializer_class = PageSerializer

    def get_queryset(self):
        """
        Filter to only return pages.
        """
        queryset = super().get_queryset()
        return queryset.filter(post_type__key="page")

    def perform_create(self, serializer):
        """
        Ensure pages are created with the correct post type.
        Create the 'page' post type if it doesn't exist for this store.
        """
        slug = serializer.validated_data.get("slug")

        # Get or create the 'page' post type for this store
        post_type, created = PostType.objects.get_or_create(
            store=self.store,
            key="page",
            defaults={
                "name": "Page",
                "description": "Static pages",
                "is_builtin": True,
                "is_active": True,
            },
        )

        # Validate slug uniqueness before saving
        if slug:
            existing_post = Post.objects.filter(
                store=self.store, post_type=post_type, slug=slug
            ).exists()
            if existing_post:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    {"slug": ["A page with this slug already exists for this store."]}
                )

        # Set the post type in validated data
        serializer.validated_data["post_type"] = post_type
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class BlogViewSet(PostViewSet):
    """
    ViewSet for managing blog posts (posts with post_type.key='blog').
    """

    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Filter to only return blog posts.
        """
        queryset = super().get_queryset()
        return queryset.filter(post_type__key="blog")

    def perform_create(self, serializer):
        """
        Ensure blog posts are created with the correct post type.
        Create the 'blog' post type if it doesn't exist for this store.
        """
        # Get or create the 'blog' post type for this store
        post_type, created = PostType.objects.get_or_create(
            store=self.store,
            key="blog",
            defaults={
                "name": "Blog",
                "description": "Blog posts",
                "is_builtin": True,
                "is_active": True,
                "allow_categories": True,
                "allow_tags": True,
                "allow_comments": True,
            },
        )

        # Set the post type in validated data
        serializer.validated_data["post_type"] = post_type

        # Pass post_type to serializer context for validation
        serializer.context["post_type"] = post_type

        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class PolicyViewSet(PostViewSet):
    """
    ViewSet for managing policy pages (posts with post_type.key='policy').
    """

    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Filter to only return policy pages.
        """
        queryset = super().get_queryset()
        return queryset.filter(post_type__key="policy")

    def perform_create(self, serializer):
        """
        Ensure policy pages are created with the correct post type.
        Create the 'policy' post type if it doesn't exist for this store.
        """
        # Get or create the 'policy' post type for this store
        post_type, created = PostType.objects.get_or_create(
            store=self.store,
            key="policy",
            defaults={
                "name": "Policy",
                "description": "Policy pages",
                "is_builtin": True,
                "is_active": True,
                "allow_categories": False,
                "allow_tags": False,
                "allow_comments": False,
            },
        )

        # Set the post type in validated data
        serializer.validated_data["post_type"] = post_type

        # Pass post_type to serializer context for validation
        serializer.context["post_type"] = post_type

        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class CategoryViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active", "parent"]  # Removed 'store' as we filter in get_queryset
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "slug", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Filter categories by store.
        """
        return Category.objects.select_related("parent").filter(store=self.store)

    def perform_create(self, serializer):
        """
        Create category for the specified store.
        """
        serializer.save(store=self.store)

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """
        Get posts for this category.
        """
        category = self.get_object()
        posts = category.posts.filter(status="published").order_by("-published_at")

        # Optional post_type filter
        post_type_key = request.query_params.get("post_type_key")
        if post_type_key:
            posts = posts.filter(post_type__key=post_type_key)

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)


class TagViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing tags.
    """

    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "slug", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Tag.objects.all().filter(store=self.store)

    def get_serializer_context(self):
        """
        Add the request to the serializer context.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        """
        Create tag for the specified store.
        """
        serializer.save(store=self.store)

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """
        Get posts for this tag.
        """
        tag = self.get_object()
        posts = tag.posts.filter(status="published").order_by("-published_at")

        # Optional post_type filter
        post_type_key = request.query_params.get("post_type_key")
        if post_type_key:
            posts = posts.filter(post_type__key=post_type_key)

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)


class CommentViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["post", "user", "parent", "is_approved", "is_public"]
    search_fields = ["content"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        """
        Filter comments by store.
        """
        return Comment.objects.select_related("user", "post", "parent").filter(
            post__store=self.store
        )

    def perform_create(self, serializer):
        """
        Create comment with proper store scoping.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Only allow comment owner or store admin to update comments.
        For now, allow any authenticated user to update (in production, check ownership).
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Only allow comment owner or store admin to delete comments.
        For now, allow any authenticated user to delete (in production, check ownership).
        """
        instance.delete()

    @action(detail=False, methods=["get"])
    def by_post(self, request):
        """
        Get comments for a specific post.
        """
        post_id = request.query_params.get("post")
        if not post_id:
            return Response(
                {"error": "post parameter is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has access to this post's store
        # For now, allow all authenticated users

        comments = (
            Comment.objects.filter(post=post, is_public=True, is_approved=True)
            .select_related("user", "parent")
            .order_by("created_at")
        )

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class PostMetaViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing post metadata.
    """

    serializer_class = PostMetaSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["post", "key"]
    ordering_fields = ["key", "created_at", "updated_at"]
    ordering = ["key"]

    def get_queryset(self):
        """
        Filter post metadata by store.
        """
        return PostMeta.objects.select_related("post").filter(post__store=self.store)

    def perform_create(self, serializer):
        """
        Create metadata for a post.
        """
        serializer.save()


class PostTypeTemplateViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing PostTypeTemplate mappings - which template to use for each post type under each theme.
    """

    serializer_class = PostTypeTemplateSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["post_type", "theme", "template"]
    ordering_fields = ["post_type__name", "theme__name", "template__name"]
    ordering = ["post_type__name", "theme__name"]

    def get_queryset(self):
        """
        Filter PostTypeTemplate mappings by store.
        """
        return PostTypeTemplate.objects.select_related("post_type", "theme", "template").filter(
            store=self.store
        )

    def perform_create(self, serializer):
        """
        Create PostTypeTemplate mapping for the current store.
        """
        serializer.save(store=self.store)

    def perform_update(self, serializer):
        """
        Update PostTypeTemplate mapping.
        """
        serializer.save()
