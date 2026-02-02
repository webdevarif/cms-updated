"""
Store management services for Digital Farmers CMS.

Shared store management service.
"""

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

logger = logging.getLogger(__name__)


class StoreService:
    """Shared store management service"""

    @staticmethod
    def create_store(name, slug, owner=None, **extra_fields):
        """
        Centralized store creation method
        Replaces all direct Store.objects.create() calls
        """
        from apps.stores.models import Store

        return Store.objects.create(name=name, slug=slug, owner=owner, **extra_fields)

    @staticmethod
    def get_store(slug=None, store_id=None, **filters):
        """
        Centralized store retrieval method
        Replaces all direct Store.objects.get() calls
        """
        from apps.stores.models import Store

        if slug:
            return Store.objects.get(slug=slug, **filters)
        elif store_id:
            return Store.objects.get(id=store_id, **filters)
        else:
            return Store.objects.get(**filters)

    @staticmethod
    def get_store_or_none(slug=None, store_id=None, **filters):
        """
        Centralized store retrieval method (safe)
        """
        from apps.stores.models import Store

        if slug:
            return Store.objects.filter(slug=slug, **filters).first()
        elif store_id:
            return Store.objects.filter(id=store_id, **filters).first()
        else:
            return Store.objects.filter(**filters).first()

    @staticmethod
    def update_store(store, **fields):
        """
        Centralized store update method
        Replaces all direct store.save() calls
        """
        for field, value in fields.items():
            setattr(store, field, value)
        store.save()
        return store

    @staticmethod
    def delete_store(store):
        """
        Centralized store deletion method
        Replaces all direct store.delete() calls
        """
        store.delete()

    @staticmethod
    def filter_stores(**filters):
        """
        Centralized store filtering method
        Replaces all direct Store.objects.filter() calls
        """
        from apps.stores.models import Store

        return Store.objects.filter(**filters)
