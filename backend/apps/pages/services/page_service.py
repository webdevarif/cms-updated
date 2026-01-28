"""
Page services with caching integration for Digital Farmers CMS.

Business logic for page management with cache optimization.
"""
import logging

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PageService:
    """Page management service with caching"""

    @staticmethod
    def get_page(store, page_id):
        """
        Get page with caching
        """
        from core.services.cache_service import CacheService

        from ..models import Post

        # Try cache first
        cached = CacheService.get_json(store, "pages", "page", page_id)
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
        CacheService.cache_json(store, "pages", "page", page_id, data, timeout=3600)
        logger.debug(f"Cached page {page_id} for store {store.slug}")

        return data

    @staticmethod
    def get_page_by_slug(store, slug):
        """
        Get page by slug with caching
        """
        from core.services.cache_service import CacheService

        from ..models import Post

        # Try cache first
        cached = CacheService.get_json(store, "pages", "page_by_slug", slug)
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
        CacheService.cache_json(store, "pages", "page_by_slug", slug, data, timeout=3600)
        logger.debug(f"Cached page slug {slug} for store {store.slug}")

        return data

    @staticmethod
    def get_published_pages(store):
        """
        Get all published pages for a store with caching
        """
        from core.services.cache_service import CacheService

        from ..models import Post

        # Try cache first
        cached = CacheService.get_json(store, "pages", "published_pages_list", "all")
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
                "featured_image": page.featured_image.url if page.featured_image else None,
                "url": page.get_absolute_url(),
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
            }
            data.append(page_data)

        # Cache the result
        CacheService.cache_json(store, "pages", "published_pages_list", "all", data, timeout=1800)
        logger.debug(f"Cached published pages list for store {store.slug}")

        return data

    @staticmethod
    def create_page(store, title, slug, content, **kwargs):
        """
        Create a new page
        """
        from core.services.cache_service import CacheService

        from ..models import Post

        # Create page
        page = Post.objects.create(
            store=store, title=title, slug=slug, content=content, status="draft", **kwargs
        )

        # Invalidate page cache
        CacheService.delete(store, "pages", "page", str(page.id))
        CacheService.delete(store, "pages", "page_by_slug", slug)
        CacheService.delete_pattern(store, "pages:published_pages_list:*")

        logger.info(f"Created page {page.id} for store {store.slug}")

        return page

    @staticmethod
    def update_page(page, **kwargs):
        """
        Update a page
        """
        from core.services.cache_service import CacheService

        # Update page
        for field, value in kwargs.items():
            setattr(page, field, value)
        page.save()

        # Invalidate cache
        CacheService.delete(page.store, "pages", "page", str(page.id))
        CacheService.delete(page.store, "pages", "page_by_slug", page.slug)
        CacheService.invalidate_module(page.store, "pages")

        # If status changed to published, invalidate all page listings
        if "status" in kwargs and kwargs["status"] == "published":
            CacheService.invalidate_module(page.store, "pages")

        logger.info(f"Updated page {page.id} for store {page.store.slug}")

        return page

    @staticmethod
    def delete_page(page):
        """
        Delete a page
        """
        from core.services.cache_service import CacheService

        # Invalidate cache
        CacheService.delete(page.store, "pages", "page", str(page.id))
        CacheService.delete(page.store, "pages", "page_by_slug", page.slug)
        CacheService.invalidate_module(page.store, "pages")

        # Delete page
        page.delete()

        logger.info(f"Deleted page {page.id} for store {page.store.slug}")

        return True
