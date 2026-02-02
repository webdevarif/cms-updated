import time

from apps.ecommerce.models import Product
from apps.posts.models import Post
from django.db.models import Q


class SimpleSearchService:
    @staticmethod
    def search(query, store, limit=20, offset=0, content_types=None, user=None, request=None):
        start_time = time.time()
        results = []
        total = 0

        if "post" in content_types or not content_types:
            posts = Post.objects.filter(store=store, status="published").filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )[offset : offset + limit]
            for p in posts:
                results.append(
                    {
                        "id": p.id,
                        "type": "post",
                        "title": p.title,
                        "url": p.get_absolute_url(),
                        "excerpt": p.excerpt,
                    }
                )
            total += (
                Post.objects.filter(store=store, status="published")
                .filter(Q(title__icontains=query) | Q(content__icontains=query))
                .count()
            )

        if "page" in content_types or not content_types:
            pages = Post.objects.filter(
                store=store, status="published", post_type__slug="page"
            ).filter(Q(title__icontains=query) | Q(content__icontains=query))[
                offset : offset + limit
            ]
            for p in pages:
                results.append(
                    {
                        "id": p.id,
                        "type": "page",
                        "title": p.title,
                        "url": p.get_absolute_url(),
                        "excerpt": p.excerpt,
                    }
                )
            total += (
                Post.objects.filter(store=store, status="published", post_type__slug="page")
                .filter(Q(title__icontains=query) | Q(content__icontains=query))
                .count()
            )

        if "product" in content_types or not content_types:
            products = Product.objects.filter(store=store, is_active=True).filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )[offset : offset + limit]
            for p in products:
                results.append(
                    {
                        "id": p.id,
                        "type": "product",
                        "title": p.title,
                        "url": p.get_absolute_url(),
                        "excerpt": p.description,
                    }
                )
            total += (
                Product.objects.filter(store=store, is_active=True)
                .filter(Q(title__icontains=query) | Q(description__icontains=query))
                .count()
            )

        duration_ms = int((time.time() - start_time) * 1000)

        # Log the search via EventService
        from .event_service import EventService

        EventService.log_search(query, total, duration_ms, request, user, store)

        return {
            "results": results,
            "total": total,
            "facets": {},
            "highlighting": {},
            "suggestions": [],
            "duration_ms": duration_ms,
        }

    @staticmethod
    def get_suggestions(store, query, limit=10):
        suggestions = list(
            set(
                list(
                    Post.objects.filter(store=store, status="published")
                    .filter(Q(title__istartswith=query) | Q(post_type__slug="page"))
                    .values_list("title", flat=True)
                )[:limit]
                + list(
                    Post.objects.filter(store=store, status="published", post_type__slug="page")
                    .filter(title__istartswith=query)
                    .values_list("title", flat=True)
                )[:limit]
                + list(
                    Product.objects.filter(store=store, is_active=True)
                    .filter(title__istartswith=query)
                    .values_list("title", flat=True)
                )[:limit]
            )
        )[:limit]
        return suggestions

    @staticmethod
    def get_facets(store, query=None):
        # Basic facets, return empty for now
        return {}
