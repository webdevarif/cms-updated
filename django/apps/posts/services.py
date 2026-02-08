from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify

from .models import Category, Post, PostMeta, PostType, PostTypeTemplate, Tag


def create_builtin_post_types_for_store(store):
    """
    Ensure that builtin post types (post, page, blog, policy) exist for a store.

    Args:
        store: Store instance

    Returns:
        dict: Created or existing builtin post types
    """
    builtins = {}

    # Create or get 'post' type
    post_type, created = PostType.objects.get_or_create(
        store=store,
        key="post",
        defaults={
            "name": "Post",
            "description": "Standard blog posts",
            "is_builtin": True,
            "is_active": True,
            "allow_categories": True,
            "allow_tags": True,
            "allow_comments": True,
        },
    )
    builtins["post"] = post_type

    # Create or get 'page' type
    page_type, created = PostType.objects.get_or_create(
        store=store,
        key="page",
        defaults={
            "name": "Page",
            "description": "Static pages",
            "is_builtin": True,
            "is_active": True,
            "allow_categories": False,
            "allow_tags": False,
            "allow_comments": False,
        },
    )
    builtins["page"] = page_type

    # Create or get 'blog' type
    blog_type, created = PostType.objects.get_or_create(
        store=store,
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
    builtins["blog"] = blog_type

    # Create or get 'policy' type
    policy_type, created = PostType.objects.get_or_create(
        store=store,
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
    builtins["policy"] = policy_type

    return builtins


def create_post(store, post_type_key, data, author=None):
    """
    Create a new post with proper validation and defaults.

    Args:
        store: Store instance
        post_type_key: Key of the post type
        data: dict with post data
        author: User instance (optional, for future audit)

    Returns:
        Post instance

    Raises:
        ValidationError: If post_type doesn't exist or validation fails
    """
    try:
        post_type = PostType.objects.get(store=store, key=post_type_key, is_active=True)
    except PostType.DoesNotExist:
        raise ValidationError(f"Post type '{post_type_key}' not found or inactive for this store")

    # Prepare post data
    post_data = {
        "store": store,
        "post_type": post_type,
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "content_type": data.get("content_type", "html"),
        "status": data.get("status", "draft"),
        "is_featured": data.get("is_featured", False),
    }

    # Optional fields
    if "slug" in data:
        post_data["slug"] = data["slug"]
    if "excerpt" in data:
        post_data["excerpt"] = data["excerpt"]
    if "published_at" in data:
        post_data["published_at"] = data["published_at"]

    # Create post
    post = Post.objects.create(**post_data)

    # Handle metadata if provided
    meta_data = data.get("meta", [])
    if meta_data:
        for meta_item in meta_data:
            PostMeta.objects.create(post=post, key=meta_item["key"], value=meta_item["value"])

    return post


def get_published_posts(store, post_type_key=None, filters=None, ordering=None):
    """
    Get published posts for a store, optionally filtered by post type.

    Args:
        store: Store instance
        post_type_key: Optional post type key to filter by
        filters: Optional dict of additional filters
        ordering: Optional list of ordering fields

    Returns:
        QuerySet of published Post objects
    """
    queryset = Post.objects.filter(
        store=store, status="published", published_at__lte=timezone.now()
    )

    if post_type_key:
        queryset = queryset.filter(post_type__key=post_type_key)

    if filters:
        queryset = queryset.filter(**filters)

    if ordering:
        queryset = queryset.order_by(*ordering)
    else:
        queryset = queryset.order_by("-published_at")

    return queryset


def get_post_by_slug(store, post_type_key, slug):
    """
    Get a published post by slug.

    Args:
        store: Store instance
        post_type_key: Post type key
        slug: Post slug

    Returns:
        Post instance or None
    """
    try:
        return Post.objects.get(
            store=store,
            post_type__key=post_type_key,
            slug=slug,
            status="published",
            published_at__lte=timezone.now(),
        )
    except Post.DoesNotExist:
        return None


def update_post_meta(post, meta_dict):
    """
    Update metadata for a post. Existing keys are updated, new keys are created.

    Args:
        post: Post instance
        meta_dict: dict of key-value pairs
    """
    for key, value in meta_dict.items():
        PostMeta.objects.update_or_create(post=post, key=key, defaults={"value": value})


def delete_post_meta(post, keys):
    """
    Delete specific metadata keys for a post.

    Args:
        post: Post instance
        keys: List of keys to delete
    """
    PostMeta.objects.filter(post=post, key__in=keys).delete()


def get_post_type_usage(post_type):
    """
    Get usage statistics for a post type.

    Args:
        post_type: PostType instance

    Returns:
        dict: Usage statistics
    """
    posts = post_type.posts.all()
    total_posts = posts.count()
    published_posts = posts.filter(status="published").count()
    draft_posts = posts.filter(status="draft").count()
    archived_posts = posts.filter(status="archived").count()

    return {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "archived_posts": archived_posts,
    }


def bulk_update_post_status(posts, new_status, published_at=None):
    """
    Bulk update status for multiple posts.

    Args:
        posts: QuerySet or list of Post instances
        new_status: New status value
        published_at: Optional published_at timestamp for published status
    """
    update_data = {"status": new_status}

    if new_status == "published" and published_at:
        update_data["published_at"] = published_at
    elif new_status != "published":
        update_data["published_at"] = None

    posts.update(**update_data)


def validate_post_slug_uniqueness(store, post_type, slug, exclude_post=None):
    """
    Validate that a slug is unique within a store and post type.

    Args:
        store: Store instance
        post_type: PostType instance
        slug: Slug to validate
        exclude_post: Optional Post instance to exclude from check

    Returns:
        bool: True if valid, raises ValidationError if not
    """
    queryset = Post.objects.filter(store=store, post_type=post_type, slug=slug)

    if exclude_post:
        queryset = queryset.exclude(pk=exclude_post.pk)

    if queryset.exists():
        raise ValidationError(
            f"Post with slug '{slug}' already exists for this store and post type"
        )

    return True


def create_or_get_category(store, name, slug=None, **kwargs):
    """
    Create or get a category for a store.

    Args:
        store: Store instance
        name: Category name
        slug: Optional slug, auto-generated from name if not provided
        **kwargs: Additional fields (description, parent, is_active)

    Returns:
        Category instance

    Raises:
        ValidationError: If category creation fails
    """
    if not slug:
        slug = slugify(name)

    category, created = Category.objects.get_or_create(
        store=store, slug=slug, defaults={"name": name, **kwargs}
    )

    # Update existing category if additional fields provided
    if not created and kwargs:
        for key, value in kwargs.items():
            setattr(category, key, value)
        category.save()

    return category


def create_or_get_tag(store, name, slug=None, **kwargs):
    """
    Create or get a tag for a store.

    Args:
        store: Store instance
        name: Tag name
        slug: Optional slug, auto-generated from name if not provided
        **kwargs: Additional fields (description, is_active)

    Returns:
        Tag instance

    Raises:
        ValidationError: If tag creation fails
    """
    if not slug:
        slug = slugify(name)

    tag, created = Tag.objects.get_or_create(
        store=store, slug=slug, defaults={"name": name, **kwargs}
    )

    # Update existing tag if additional fields provided
    if not created and kwargs:
        for key, value in kwargs.items():
            setattr(tag, key, value)
        tag.save()

    return tag


def assign_categories_to_post(post, category_slugs_or_ids):
    """
    Assign categories to a post, ensuring store consistency.

    Args:
        post: Post instance
        category_slugs_or_ids: List of category slugs or IDs

    Returns:
        QuerySet of assigned categories

    Raises:
        ValidationError: If categories don't belong to the same store
    """
    if not category_slugs_or_ids:
        post.categories.clear()
        return post.categories.all()

    # Get categories by slug or ID, filtered by store
    categories = []
    for identifier in category_slugs_or_ids:
        try:
            # Try as ID first
            category = Category.objects.get(store=post.store, pk=int(identifier), is_active=True)
        except (ValueError, Category.DoesNotExist):
            # Try as slug
            try:
                category = Category.objects.get(store=post.store, slug=identifier, is_active=True)
            except Category.DoesNotExist:
                raise ValidationError(
                    f"Category '{identifier}' not found or inactive for this store"
                )

        categories.append(category)

    # Assign categories
    post.categories.set(categories)
    return post.categories.all()


def assign_tags_to_post(post, tag_slugs_or_ids):
    """
    Assign tags to a post, ensuring store consistency.

    Args:
        post: Post instance
        tag_slugs_or_ids: List of tag slugs or IDs

    Returns:
        QuerySet of assigned tags

    Raises:
        ValidationError: If tags don't belong to the same store
    """
    if not tag_slugs_or_ids:
        post.tags.clear()
        return post.tags.all()

    # Get tags by slug or ID, filtered by store
    tags = []
    for identifier in tag_slugs_or_ids:
        try:
            # Try as ID first
            tag = Tag.objects.get(store=post.store, pk=int(identifier), is_active=True)
        except (ValueError, Tag.DoesNotExist):
            # Try as slug
            try:
                tag = Tag.objects.get(store=post.store, slug=identifier, is_active=True)
            except Tag.DoesNotExist:
                raise ValidationError(f"Tag '{identifier}' not found or inactive for this store")

        tags.append(tag)

    # Assign tags
    post.tags.set(tags)
    return post.tags.all()


def create_comment(store, post, user, content, parent=None):
    """
    Create a comment on a post.

    Args:
        store: Store instance (must match post.store)
        post: Post instance to comment on
        user: User instance making the comment
        content: Comment content
        parent: Optional parent Comment instance for replies

    Returns:
        Comment instance

    Raises:
        ValidationError: If validation fails
    """
    from .models import Comment

    # Validate store consistency
    if store != post.store:
        raise ValidationError("Comment store must match post store")

    # Create comment
    comment = Comment.objects.create(
        store=store, post=post, user=user, content=content, parent=parent
    )

    return comment


def get_post_comments(post, include_replies=True):
    """
    Get comments for a post, optionally including threaded replies.

    Args:
        post: Post instance
        include_replies: Whether to include reply structure

    Returns:
        QuerySet of comments
    """
    if include_replies:
        # Return all comments for the post (replies will be nested in serializer)
        return (
            Comment.objects.filter(post=post, is_public=True, is_approved=True)
            .select_related("user", "parent")
            .order_by("created_at")
        )
    else:
        # Return only top-level comments
        return (
            Comment.objects.filter(post=post, parent__isnull=True, is_public=True, is_approved=True)
            .select_related("user")
            .order_by("created_at")
        )


def get_posts_by_category(store, category_slug_or_id, post_type_key=None):
    """
    Get posts for a specific category.

    Args:
        store: Store instance
        category_slug_or_id: Category slug or ID
        post_type_key: Optional post type key to filter

    Returns:
        QuerySet of posts
    """
    try:
        # Try as ID first
        category = Category.objects.get(store=store, pk=int(category_slug_or_id), is_active=True)
    except (ValueError, Category.DoesNotExist):
        # Try as slug
        category = Category.objects.get(store=store, slug=category_slug_or_id, is_active=True)

    posts = category.posts.filter(status="published")

    if post_type_key:
        posts = posts.filter(post_type__key=post_type_key)

    return posts.order_by("-published_at")


def get_posts_by_tag(store, tag_slug_or_id, post_type_key=None):
    """
    Get posts for a specific tag.

    Args:
        store: Store instance
        tag_slug_or_id: Tag slug or ID
        post_type_key: Optional post type key to filter

    Returns:
        QuerySet of posts
    """
    try:
        # Try as ID first
        tag = Tag.objects.get(store=store, pk=int(tag_slug_or_id), is_active=True)
    except (ValueError, Tag.DoesNotExist):
        # Try as slug
        tag = Tag.objects.get(store=store, slug=tag_slug_or_id, is_active=True)

    posts = tag.posts.filter(status="published")

    if post_type_key:
        posts = posts.filter(post_type__key=post_type_key)

    return posts.order_by("-published_at")


def get_or_create_post_type_template(store, post_type, theme):
    """
    Return the Template to use for this store/post_type/theme.

    Behavior:
      1. If a PostTypeTemplate exists, return its .template (can be None).
      2. If not, create a PostTypeTemplate with a sensible default Template for that theme
         and return that Template.

    Args:
        store: Store instance
        post_type: PostType instance
        theme: Theme instance

    Returns:
        themes.Template instance or None
    """
    from apps.themes.models import Template as ThemeTemplate

    mapping, created = PostTypeTemplate.objects.get_or_create(
        store=store,
        post_type=post_type,
        theme=theme,
        defaults={"template": None},
    )

    if mapping.template:
        return mapping.template

    # Pick a sensible default from this theme:
    # e.g. first active body template, or a known key like "page-default"/"blog-default"
    default_qs = ThemeTemplate.objects.filter(theme=theme, is_active=True, template_role="body")

    # For body templates, filter by template_type compatibility:
    # - Prefer templates with matching template_type (e.g. "page" for pages)
    # - Fall back to "any" templates if no specific match
    from django.db.models import Q

    default_qs = default_qs.filter(
        Q(template_type=post_type.key) | Q(template_type="any")
    ).order_by("name")

    default_template = default_qs.first()

    if default_template and mapping.template != default_template:
        mapping.template = default_template
        mapping.save(update_fields=["template"])

    return mapping.template
