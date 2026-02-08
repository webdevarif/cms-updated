from apps.stores.models import Store
from rest_framework import serializers

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Category, Comment, Post, PostMeta, PostType, PostTypeTemplate, Tag


class PostTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for PostType model.
    """

    post_count = serializers.SerializerMethodField(read_only=True)
    current_theme_template = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostType
        fields = [
            "id",
            "store",
            "name",
            "key",
            "description",
            "is_builtin",
            "is_active",
            "schema",
            "post_count",
            "current_theme_template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_post_count(self, obj):
        return obj.posts.count()

    def get_current_theme_template(self, obj):
        """
        Return the selected body template for this post type's store under the active theme.
        """
        from apps.themes.models import Theme

        from .services import get_or_create_post_type_template

        # Get the active (default) theme for this store
        active_theme = Theme.objects.filter(store=obj.store, is_default=True).first()

        if not active_theme:
            return None

        # Get the template for this post_type under the active theme
        template = get_or_create_post_type_template(obj.store, obj, active_theme)

        if not template or template.template_role != "body":
            return None

        return {
            "id": template.id,
            "name": template.name,
            "key": template.key,
            "template_role": template.template_role,
            "theme_id": template.theme_id,
        }

    def validate_key(self, value):
        if self.instance and self.instance.is_builtin:
            if value not in ["post", "page"]:
                raise serializers.ValidationError("Cannot change key of builtin post types")
        return value


class PostMetaSerializer(serializers.ModelSerializer):
    """
    Serializer for PostMeta model.
    """

    class Meta:
        model = PostMeta
        fields = ["id", "post", "key", "value", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """

    post_count = serializers.SerializerMethodField(read_only=True)
    full_path = serializers.CharField(read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "store",
            "name",
            "slug",
            "description",
            "parent",
            "parent_name",
            "full_path",
            "is_active",
            "post_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_path"]

    def get_post_count(self, obj):
        return obj.posts.count()

    def validate_parent(self, value):
        """
        Ensure parent category belongs to the same store and prevent circular references.
        """
        if value and hasattr(self, "instance") and self.instance:
            if value.store != self.instance.store:
                raise serializers.ValidationError("Parent category must belong to the same store")
            if value == self.instance:
                raise serializers.ValidationError("A category cannot be its own parent")
            if value.parent == self.instance:
                raise serializers.ValidationError("Circular reference in category hierarchy")
        elif value and self.initial_data.get("store"):
            store_id = self.initial_data["store"]
            if isinstance(store_id, dict):
                store_id = store_id.get("id")
            if value.store_id != store_id:
                raise serializers.ValidationError("Parent category must belong to the same store")
        return value


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """

    post_count = serializers.SerializerMethodField(read_only=True)
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=False,  # Not required in input, will be set from request
        write_only=True,  # Don't include in output, it's already in the URL/context
    )

    class Meta:
        model = Tag
        fields = [
            "id",
            "store",
            "name",
            "slug",
            "description",
            "is_active",
            "post_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_post_count(self, obj):
        return obj.posts.count()

    def create(self, validated_data):
        # If store is not provided in the request data, try to get it from the context
        if "store" not in validated_data and hasattr(self.context.get("request"), "store_id"):
            from apps.stores.models import Store

            from django.shortcuts import get_object_or_404

            store_id = self.context["request"].store_id
            validated_data["store"] = get_object_or_404(Store, id=store_id)

        return super().create(validated_data)

    def validate(self, data):
        # Add any additional validation here
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model with optional nested replies.
    """

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    is_reply = serializers.BooleanField(read_only=True)
    parent_content_preview = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "store",
            "post",
            "user",
            "user_name",
            "user_email",
            "parent",
            "parent_content_preview",
            "content",
            "is_reply",
            "replies",
            "is_approved",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_name", "user_email", "is_reply"]

    def get_replies(self, obj):
        """
        Get nested replies for this comment.
        """
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def get_parent_content_preview(self, obj):
        """
        Get a preview of the parent comment content.
        """
        if obj.parent:
            content = obj.parent.content
            return content[:100] + "..." if len(content) > 100 else content
        return None

    def validate_post(self, value):
        """
        Ensure comment store matches post store.
        """
        if hasattr(self, "initial_data") and "store" in self.initial_data:
            store_id = self.initial_data["store"]
            if isinstance(store_id, dict):
                store_id = store_id.get("id")
            if value.store_id != store_id:
                raise serializers.ValidationError("Comment store must match post store")
        return value

    def validate_parent(self, value):
        """
        Ensure parent comment belongs to the same post and prevent deep nesting.
        """
        if value:
            if hasattr(self, "initial_data") and "post" in self.initial_data:
                post_id = self.initial_data["post"]
                if isinstance(post_id, dict):
                    post_id = post_id.get("id")
                if value.post_id != post_id:
                    raise serializers.ValidationError("Parent comment must belong to the same post")

            # Prevent replies to replies (only one level deep)
            if value.parent:
                raise serializers.ValidationError("Comments can only be nested one level deep")

        return value

    def validate(self, attrs):
        """
        Validate comment creation against post_type feature flags.
        """
        attrs = super().validate(attrs)

        post = attrs.get("post")
        if post and hasattr(post, "post_type"):
            if not post.post_type.allow_comments:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            f"Comments are not allowed for {post.post_type.name} posts."
                        ]
                    }
                )

        return attrs


class PostTypeTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for PostTypeTemplate model - manages which template is used for each post type under each theme.
    """

    post_type_name = serializers.CharField(source="post_type.name", read_only=True)
    theme_name = serializers.CharField(source="theme.name", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True)
    template_key = serializers.CharField(source="template.key", read_only=True)
    template_role = serializers.CharField(source="template.template_role", read_only=True)
    template_type = serializers.CharField(source="template.template_type", read_only=True)

    class Meta:
        model = PostTypeTemplate
        fields = [
            "id",
            "store",
            "post_type",
            "post_type_name",
            "theme",
            "theme_name",
            "template",
            "template_name",
            "template_key",
            "template_role",
            "template_type",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        """Validate that template belongs to the selected theme and has compatible template_type"""
        template = attrs.get("template")
        theme = attrs.get("theme")
        post_type = attrs.get("post_type")

        if template and theme and template.theme != theme:
            raise serializers.ValidationError("Template must belong to the selected theme")

        # Ensure theme and store consistency
        if theme and hasattr(theme, "store") and theme.store != attrs.get("store"):
            raise serializers.ValidationError("Theme must belong to the same store")

        # Validate template_type compatibility for body templates
        if template and template.template_role == "body" and post_type:
            # Template must have matching template_type or be "any"
            if template.template_type not in [post_type.key, "any"]:
                raise serializers.ValidationError(
                    f"Template type '{template.template_type}' is not compatible with post type '{post_type.key}'. "
                    f"Template type must be '{post_type.key}' or 'any'."
                )

        return attrs


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.
    """

    meta = PostMetaSerializer(many=True, read_only=True)
    post_type_name = serializers.CharField(source="post_type.name", read_only=True)
    post_type_key = serializers.CharField(source="post_type.key", read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    template = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "store",
            "post_type",
            "post_type_name",
            "post_type_key",
            "title",
            "slug",
            "excerpt",
            "content",
            "content_type",
            "status",
            "is_featured",
            "categories",
            "tags",
            "comments_count",
            "meta",
            "published_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "template",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_public=True, is_approved=True).count()

    def get_created_by(self, obj):
        """
        Return user object for created_by field.
        """
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "email": obj.created_by.email,
                "display_name": obj.created_by.get_full_name() or obj.created_by.username,
            }
        return None

    def get_updated_by(self, obj):
        """
        Return user object for updated_by field.
        """
        if obj.updated_by:
            return {
                "id": obj.updated_by.id,
                "username": obj.updated_by.username,
                "email": obj.updated_by.email,
                "display_name": obj.updated_by.get_full_name() or obj.updated_by.username,
            }
        return None

    def get_template(self, obj):
        """
        Return the selected body template for this post's store and post_type under the active theme.
        """
        from apps.themes.models import Theme

        from .services import get_or_create_post_type_template

        # Get the active (default) theme for this store
        active_theme = Theme.objects.filter(store=obj.store, is_default=True).first()

        if not active_theme:
            return None

        # Get the template for this post_type under the active theme
        template = get_or_create_post_type_template(obj.store, obj.post_type, active_theme)

        if not template or template.template_role != "body":
            return None

        return {
            "id": template.id,
            "name": template.name,
            "key": template.key,
            "template_role": template.template_role,
            "template_type": template.template_type,
            "theme_id": template.theme_id,
        }

    def validate_slug(self, value):
        """
        Ensure slug is unique within store and post_type.
        """
        # Get store and post_type for validation
        store = self.instance.store if self.instance else self.initial_data.get("store")
        post_type_data = (
            self.instance.post_type if self.instance else self.initial_data.get("post_type")
        )

        # Handle post_type - could be an ID, PostType object, or string key
        post_type = None
        if isinstance(post_type_data, PostType):
            post_type = post_type_data
        elif isinstance(post_type_data, str):
            # If it's a string, try to treat it as a post_type key
            try:
                post_type = PostType.objects.get(store=store, key=post_type_data)
            except (PostType.DoesNotExist, ValueError):
                # If it's not a valid key, try to treat it as an ID
                try:
                    post_type = PostType.objects.get(id=int(post_type_data))
                except (PostType.DoesNotExist, ValueError):
                    pass
        else:
            # Assume it's an ID
            try:
                post_type = PostType.objects.get(id=post_type_data)
            except (PostType.DoesNotExist, ValueError):
                pass

        # If we couldn't resolve post_type, we'll skip the uniqueness check
        # This allows the validation to pass and let perform_create handle it
        if not post_type:
            return value

        queryset = Post.objects.filter(store=store, post_type=post_type, slug=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A post with this slug already exists for this store and post type."
            )

        return value

    def validate_published_at(self, value):
        """
        Ensure published_at is not in the future for published posts.
        """
        if value and value > timezone.now() and self.initial_data.get("status") == "published":
            raise serializers.ValidationError(
                "Published posts cannot have a future publication date."
            )
        return value


class PostCreateSerializer(PostSerializer):
    """
    Serializer for creating posts (regular posts with post_type.key='post').
    Post type is automatically set to 'post' by the ViewSet.
    """

    class Meta:
        model = Post
        fields = [
            "id",
            "store",
            # no 'post_type' here, it's set in the view
            "title",
            "slug",
            "excerpt",
            "content",
            "content_type",
            "status",
            "is_featured",
            "categories",
            "tags",
            "meta",
            "published_at",
            "created_at",
            "updated_at",
            "post_type_name",
            "post_type_key",
            "comments_count",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "post_type_name",
            "post_type_key",
            "comments_count",
            "created_by",
            "updated_by",
        ]

    def validate(self, attrs):
        """
        Validate post creation against post_type feature flags.
        """
        attrs = super().validate(attrs)

        # Get post_type from context (set in ViewSet perform_create)
        post_type = self.context.get("post_type")
        if not post_type:
            # Fallback: try to get from validated_data if it exists
            post_type = attrs.get("post_type")

        if post_type:
            # Check categories
            if not post_type.allow_categories and attrs.get("categories"):
                raise serializers.ValidationError(
                    {"categories": f"Categories are not allowed for {post_type.name} posts."}
                )

            # Check tags
            if not post_type.allow_tags and attrs.get("tags"):
                raise serializers.ValidationError(
                    {"tags": f"Tags are not allowed for {post_type.name} posts."}
                )

        return attrs


class PageSerializer(PostSerializer):
    """
    Serializer for pages (posts with post_type.key='page').
    Post type is automatically set to 'page' by the ViewSet.
    """

    post_type_name = serializers.CharField(source="post_type.name", read_only=True)
    post_type_key = serializers.CharField(source="post_type.key", read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    meta = PostMetaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "store",
            "post_type_name",
            "post_type_key",
            "title",
            "slug",
            "excerpt",
            "content",
            "content_type",
            "status",
            "is_featured",
            "categories",
            "tags",
            "comments_count",
            "meta",
            "published_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "template",
        ]

    def validate_slug(self, value):
        """
        Ensure slug is unique within store and post_type.
        For pages, post_type is 'page', so we can hardcode this.
        """
        # Get store from instance or initial data
        store = self.instance.store if self.instance else self.initial_data.get("store")
        if not store:
            return value  # Let it fail later if store is missing

        # For pages, post_type is always 'page'
        try:
            post_type = PostType.objects.get(store=store, key="page")
        except PostType.DoesNotExist:
            return value  # Let perform_create handle post_type creation

        queryset = Post.objects.filter(store=store, post_type=post_type, slug=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A page with this slug already exists for this store."
            )

        return value
