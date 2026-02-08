"""
Page services with caching integration for Digital Farmers CMS.

Business logic for page management with cache optimization.
"""

import logging

from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)


class PageService:
    """Page management service with caching"""

    @staticmethod
    def get_page(store, page_id):
        """
        Get page with caching
        """
        from django.core.cache import cache

        from ..models import Post

        # Try cache first
        key = f"page:{store.slug}:{page_id}"
        cached = cache.get(key)
        if cached:
            logger.debug(f"Cache HIT for page {page_id} in store {store.slug}")
            return cached

        # Fetch from database
        try:
            page = Post.objects.get(store=store, id=page_id, status="published")
        except Post.DoesNotExist:
            return None

        # Build page data
        data = {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "content": page.content,
            "excerpt": page.excerpt,
            "featured_image": page.featured_image.url if page.featured_image else None,
            "meta_title": page.meta_title or page.title,
            "meta_description": page.meta_description or "",
            "url": page.get_absolute_url(),
            "created_at": page.created_at.isoformat(),
            "updated_at": page.updated_at.isoformat(),
            "status": page.status,
        }

        # Cache the result
        cache.set(key, data, 3600)
        logger.debug(f"Cached page {page_id} for store {store.slug}")

        return data

    @staticmethod
    def get_page_by_slug(store, slug):
        """
        Get page by slug with caching
        """
        from django.core.cache import cache

        from ..models import Post

        # Try cache first
        key = f"page_slug:{store.slug}:{slug}"
        cached = cache.get(key)
        if cached:
            logger.debug(f"Cache HIT for page slug {slug} in store {store.slug}")
            return cached

        # Fetch from database
        try:
            page = Post.objects.get(store=store, slug=slug, status="published")
        except Post.DoesNotExist:
            return None

        # Build page data
        data = {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "content": page.content,
            "excerpt": page.excerpt,
            "featured_image": page.featured_image.url if page.featured_image else None,
            "meta_title": page.meta_title or page.title,
            "meta_description": page.meta_description or "",
            "url": page.get_absolute_url(),
            "created_at": page.created_at.isoformat(),
            "updated_at": page.updated_at.isoformat(),
            "status": page.status,
        }

        # Cache the result
        cache.set(key, data, 3600)
        logger.debug(f"Cached page slug {slug} for store {store.slug}")

        return data

    @staticmethod
    def get_published_pages(store):
        """
        Get all published pages for a store with caching
        """
        from django.core.cache import cache

        from ..models import Post

        # Try cache first
        key = f"published_pages:{store.slug}:all"
        cached = cache.get(key)
        if cached:
            logger.debug(f"Cache HIT for published pages list in store {store.slug}")
            return cached

        # Fetch from database
        pages = (
            Post.objects.filter(store=store, status="published")
            .order_by("-created_at")
            .select_related("store")
        )

        # Build page data
        data = []
        for page in pages:
            page_data = {
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "excerpt": page.excerpt,
                "featured_image": (page.featured_image.url if page.featured_image else None),
                "url": page.get_absolute_url(),
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
            }
            data.append(page_data)

        # Cache the result
        cache.set(key, data, 1800)
        logger.debug(f"Cached published pages list for store {store.slug}")

        return data

    @staticmethod
    def create_page(store, author, data: dict):
        """
        Create a new page with proper PAGE_TYPE_SLUG, logging, and cache invalidation.

        Args:
            store: Store instance
            author: User instance (author)
            data: Dictionary with page fields

        Returns:
            Created Post instance
        """
        from apps.analytics.services.event_service import EventService
        from apps.posts.models import PostType

        from django.core.cache import cache

        from ..models.pages import PAGE_TYPE_SLUG

        # Ensure page has proper post type
        if "post_type" not in data:
            page_type = PostType.objects.filter(slug=PAGE_TYPE_SLUG).first()
            if page_type:
                data["post_type"] = page_type
            else:
                raise ValidationError(f"Page post type '{PAGE_TYPE_SLUG}' not found")

        # Set required fields
        data.update(
            {
                "store": store,
                "author": author,
                "status": data.get("status", "draft"),
            }
        )

        # Create page
        page = Post.objects.create(**data)

        # Invalidate page cache
        cache.delete(f"page:{store.slug}:{page.id}")
        cache.delete(f"page_slug:{store.slug}:{page.slug}")
        cache.delete(f"published_pages:{store.slug}:all")

        # Log page creation
        EventService.log_event(
            event_type="PAGE_CREATED",
            event_name=f'Page created: "{page.title}"',
            properties={
                "user": author.id if author else None,
                "store": store.id,
                "entity_type": "Post",
                "entity_id": page.id,
                "page_id": str(page.id),
                "post_type": page.post_type.slug if page.post_type else None,
                "title": page.title,
                "slug": page.slug,
                "status": page.status,
            },
            user=author,
            store=store,
        )

        logger.info(f"Created page {page.id} for store {store.slug}")
        return page

    @staticmethod
    def update_page(page: Post, data: dict):
        """
        Update a page with validation, logging, and cache invalidation.

        Args:
            page: Post instance to update
            data: Dictionary with fields to update

        Returns:
            Updated Post instance
        """
        from apps.analytics.services.event_service import EventService

        from django.core.cache import cache

        # Store old values for logging
        old_status = page.status
        old_title = page.title

        # Update page
        for field, value in data.items():
            setattr(page, field, value)
        page.save()

        # Invalidate cache
        cache.delete(f"page:{page.store.slug}:{page.id}")
        cache.delete(f"page_slug:{page.store.slug}:{page.slug}")
        cache.delete(f"published_pages:{page.store.slug}:all")

        # If status changed to published, invalidate all page listings
        if "status" in data and data["status"] == "published" and old_status != "published":
            cache.delete(f"published_pages:{page.store.slug}:all")

        # Log page update
        EventService.log_event(
            event_type="PAGE_UPDATED",
            event_name=f'Page updated: "{page.title}"',
            properties={
                "user": (
                    getattr(page, "author", None).id if getattr(page, "author", None) else None
                ),
                "store": page.store.id,
                "entity_type": "Post",
                "entity_id": page.id,
                "page_id": str(page.id),
                "post_type": page.post_type.slug if page.post_type else None,
                "title": page.title,
                "old_title": old_title,
                "slug": page.slug,
                "status": page.status,
                "old_status": old_status,
                "fields_updated": list(data.keys()),
            },
            user=getattr(page, "author", None),
            store=page.store,
        )

        logger.info(f"Updated page {page.id} for store {page.store.slug}")
        return page

    @staticmethod
    def publish_page(page: Post, *, user=None):
        """
        Publish a page with published_at timestamp and logging.

        Args:
            page: Post instance to publish
            user: User performing the action (optional)

        Returns:
            Updated Post instance
        """
        from apps.analytics.services.event_service import EventService

        from django.core.cache import cache

        old_status = page.status

        # Update page status and published_at
        page.status = "published"
        page.published_at = timezone.now()
        page.save(update_fields=["status", "published_at"])

        # Invalidate cache
        cache.delete(f"page:{page.store.slug}:{page.id}")
        cache.delete(f"page_slug:{page.store.slug}:{page.slug}")
        cache.delete(f"published_pages:{page.store.slug}:all")

        # Log page publish
        EventService.log_event(
            event_type="PAGE_PUBLISHED",
            event_name=f'Page published: "{page.title}"',
            properties={
                "user": user.id if user else page.author.id,
                "store": page.store.id,
                "entity_type": "Post",
                "entity_id": page.id,
                "page_id": str(page.id),
                "post_type": page.post_type.slug if page.post_type else None,
                "title": page.title,
                "slug": page.slug,
                "old_status": old_status,
                "published_at": (page.published_at.isoformat() if page.published_at else None),
            },
            user=user or page.author,
            store=page.store,
        )

        logger.info(f"Published page {page.id} for store {page.store.slug}")
        return page

    @staticmethod
    def unpublish_page(page: Post, *, user=None):
        """
        Unpublish a page (set to draft) with logging.

        Args:
            page: Post instance to unpublish
            user: User performing the action (optional)

        Returns:
            Updated Post instance
        """
        from django.core.cache import cache

        old_status = page.status

        # Update page status
        page.status = "draft"
        page.save(update_fields=["status"])

        # Invalidate cache
        cache.delete(f"page:{page.store.slug}:{page.id}")
        cache.delete(f"page_slug:{page.store.slug}:{page.slug}")
        cache.delete(f"published_pages:{page.store.slug}:all")

        # Log page unpublish
        EventService.log_event(
            event_type="PAGE_UNPUBLISHED",
            event_name=f'Page unpublished: "{page.title}"',
            properties={
                "user": user.id if user else page.author.id,
                "store": page.store.id,
                "entity_type": "Post",
                "entity_id": page.id,
                "page_id": str(page.id),
                "old_status": old_status,
                "title": page.title,
                "slug": page.slug,
            },
            user=user or page.author,
            store=page.store,
        )

        logger.info(f"Unpublished page {page.id} for store {page.store.slug}")
        return page

    @staticmethod
    def bulk_action(store, action: str, page_ids: list[int], *, user=None, extra_data=None):
        """
        Centralized bulk operations with logging.

        Args:
            store: Store instance
            action: Action type (publish, unpublish, delete, etc.)
            page_ids: List of page IDs to operate on
            user: User performing the action (optional)
            extra_data: Additional data for complex actions (optional)

        Returns:
            Dictionary with operation results
        """
        from apps.analytics.services.event_service import EventService
        from apps.posts.models import Post

        from django.core.cache import cache
        from django.db import transaction

        if extra_data is None:
            extra_data = {}

        # Filter pages by store and IDs
        queryset = Post.objects.filter(store=store, id__in=page_ids)
        total_requested = len(page_ids)
        total_found = queryset.count()

        results = {
            "action": action,
            "total_requested": total_requested,
            "total_found": total_found,
            "success_count": 0,
            "error_count": 0,
            "errors": [],
        }

        try:
            with transaction.atomic():
                if action == "publish":
                    updated = queryset.update(status="published", published_at=timezone.now())
                    results["success_count"] = updated
                    message = f"Successfully published {updated} pages"

                elif action == "unpublish":
                    updated = queryset.update(status="draft")
                    results["success_count"] = updated
                    message = f"Successfully unpublished {updated} pages"

                elif action == "delete":
                    deleted_count, _ = queryset.delete()
                    results["success_count"] = deleted_count
                    message = f"Successfully deleted {deleted_count} pages"

                else:
                    # Handle other bulk actions as needed
                    results["success_count"] = 0
                    results["error_count"] = total_found
                    message = f"Unsupported bulk action: {action}"

                # Invalidate all page cache for this store
                cache.delete_many([f"page:{store.slug}:{page_id}" for page_id in page_ids])
                cache.delete(f"published_pages:{store.slug}:all")

                # Log bulk action
                EventService.log_event(
                    event_type="PAGE_BULK_ACTION",
                    event_name=f"Bulk {action} operation on pages",
                    properties={
                        "user": user.id if user else None,
                        "store": store.id,
                        "action": action,
                        "count": len(page_ids),
                        "page_ids": page_ids,
                    },
                    user=user,
                    store=store,
                )

                logger.info(
                    f"Bulk {action} completed: {results['success_count']}/{total_found} pages for store {store.slug}"
                )
                return {"message": message, **results}

        except Exception as e:
            results["error_count"] = total_found
            results["errors"].append(str(e))
            logger.error(f"Bulk {action} failed for store {store.slug}: {e}")
            return {"message": f"Bulk {action} failed", **results}

    @staticmethod
    def delete_page(page):
        """
        Delete a page
        """
        from django.core.cache import cache

        # Invalidate cache
        cache.delete(f"page:{page.store.slug}:{page.id}")
        cache.delete(f"page_slug:{page.store.slug}:{page.slug}")
        cache.delete(f"published_pages:{page.store.slug}:all")

        # Delete page
        page.delete()

        logger.info(f"Deleted page {page.id} for store {page.store.slug}")

        return True
