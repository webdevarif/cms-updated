"""
Tasks for search module - index optimization and maintenance.
"""
import logging
from datetime import timedelta

from apps.search.models.infrastructure import SearchIndex, SearchQuery
from apps.search.services.infrastructure import SearchService as InfrastructureSearchService
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def rebuild_search_index(self, store_id, content_types=None):
    """
    Rebuild search index for a specific store.

    Args:
        store_id: ID of the store to rebuild index for
        content_types: Optional list of content types to rebuild (default: all)
    """
    try:
        logger.info(f"Starting search index rebuild for store {store_id}")

        from apps.stores.models import Store

        store = Store.objects.get(id=store_id)

        # Rebuild index for specified content types
        if content_types:
            for content_type in content_types:
                InfrastructureSearchService.rebuild_index(store, content_type)
                logger.info(f"Rebuilt {content_type} index for store {store_id}")
        else:
            # Rebuild all content types
            InfrastructureSearchService.rebuild_index(store)
            logger.info(f"Rebuilt all indices for store {store_id}")

        # Update last rebuild timestamp
        search_index, created = SearchIndex.objects.get_or_create(
            store=store, defaults={"last_rebuild": timezone.now()}
        )
        if not created:
            search_index.last_rebuild = timezone.now()
            search_index.save()

        logger.info(f"Completed search index rebuild for store {store_id}")
        return f"Successfully rebuilt search index for store {store_id}"

    except Store.DoesNotExist:
        error_msg = f"Store {store_id} not found"
        logger.error(error_msg)
        raise self.retry(countdown=60, exc=Exception(error_msg))
    except Exception as e:
        error_msg = f"Search index rebuild failed for store {store_id}: {str(e)}"
        logger.error(error_msg)
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=2)
def optimize_search_indices(self):
    """
    Optimize search indices across all stores.
    Runs maintenance operations like index optimization, cleanup, etc.
    """
    try:
        logger.info("Starting search indices optimization")

        from apps.stores.models import Store

        active_stores = Store.objects.filter(status="active")

        optimized_count = 0
        for store in active_stores:
            try:
                # Optimize index for this store
                InfrastructureSearchService.optimize_index(store)
                optimized_count += 1
                logger.info(f"Optimized search index for store {store.id}")
            except Exception as e:
                logger.error(f"Failed to optimize index for store {store.id}: {str(e)}")
                continue

        logger.info(f"Completed search indices optimization for {optimized_count} stores")
        return f"Successfully optimized search indices for {optimized_count} stores"

    except Exception as e:
        error_msg = f"Search indices optimization failed: {str(e)}"
        logger.error(error_msg)
        raise self.retry(countdown=3600, exc=e)


@shared_task(bind=True, max_retries=1)
def cleanup_old_search_data(self, days_old=90):
    """
    Clean up old search data to maintain performance.

    Args:
        days_old: Remove data older than this many days (default: 90)
    """
    try:
        logger.info(f"Starting cleanup of search data older than {days_old} days")

        cutoff_date = timezone.now() - timedelta(days=days_old)

        # Remove old search queries
        old_queries = SearchQuery.objects.filter(created_at__lt=cutoff_date)
        old_queries_count = old_queries.count()
        old_queries.delete()

        logger.info(f"Cleaned up {old_queries_count} old search queries")
        return f"Successfully cleaned up {old_queries_count} old search records"

    except Exception as e:
        error_msg = f"Search data cleanup failed: {str(e)}"
        logger.error(error_msg)
        # Don't retry cleanup tasks as they can be run again later
        raise e


@shared_task(bind=True)
def generate_search_reports(self):
    """
    Generate daily/weekly search analytics reports.
    """
    try:
        logger.info("Starting search reports generation")

        from apps.stores.models import Store

        active_stores = Store.objects.filter(status="active")
        reports_generated = 0

        for store in active_stores:
            try:
                # Generate 30-day report
                thirty_days_ago = timezone.now() - timedelta(days=30)

                report_data = SearchQuery.objects.filter(
                    store=store, created_at__gte=thirty_days_ago
                ).aggregate(
                    total_queries=Count("id"),
                    avg_results=Avg("results_count"),
                    no_results_count=Count("id", filter=Q(results_count=0)),
                )

                # Store or email the report
                # This could be enhanced to save reports to database or send emails

                reports_generated += 1
                logger.info(f"Generated search report for store {store.id}")

            except Exception as e:
                logger.error(f"Failed to generate report for store {store.id}: {str(e)}")
                continue

        logger.info(f"Generated search reports for {reports_generated} stores")
        return f"Successfully generated search reports for {reports_generated} stores"

    except Exception as e:
        error_msg = f"Search reports generation failed: {str(e)}"
        logger.error(error_msg)
        raise e


@shared_task(bind=True, max_retries=3)
def index_document(self, store_id, document_type, document_id, data):
    """
    Async document indexing task
    """
    try:
        from apps.stores.models import Store

        from .models import SearchIndex
        from .services import SearchService

        store = Store.objects.get(id=store_id)
        result = SearchService.index_document(store, document_type, document_id, data)

        return {"document_id": document_id, "indexed": result}

    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Document indexing failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def rebuild_index(self, store_id):
    """
    Async index rebuild task
    """
    try:
        from apps.stores.models import Store

        from .models import SearchIndex
        from .services import SearchService

        store = Store.objects.get(id=store_id)
        result = SearchService.rebuild_index(store)

        return {"store_id": store_id, "rebuilt": result}

    except Store.DoesNotExist:
        logger.error(f"Store #{store_id} not found")
        return {"store_id": store_id, "rebuilt": False}

    except Exception as exc:
        logger.error(f"Index rebuild failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
