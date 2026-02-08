from rest_framework import viewsets

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Store


class StoreNotFoundError(ValidationError):
    """
    Custom exception raised when store cannot be found or is invalid.
    This will be converted to a 400 response with clear error message.
    """

    pass


def get_store_from_request(request):
    """
    Reads Store from:
    - Header: HTTP_STORE (preferred)
    - Fallback: query param `store`
    - (Optional) fallback: request.data["store"]

    Validates the store exists and is active.
    Raises StoreNotFoundError if missing/invalid.

    Args:
        request: Django REST framework request object

    Returns:
        Store: The validated Store instance

    Raises:
        StoreNotFoundError: If store is missing, invalid, or inactive
    """
    store_id = None

    # 1. Try header first (preferred method)
    if hasattr(request, "META") and "HTTP_STORE" in request.META:
        store_id = request.META.get("HTTP_STORE")

    # 2. Fallback to query parameters
    if not store_id and hasattr(request, "query_params"):
        store_id = request.query_params.get("store")

    # 3. Final fallback to request data (for explicit store selection workflows)
    if not store_id and hasattr(request, "data") and isinstance(request.data, dict):
        store_id = request.data.get("store")

    if not store_id:
        raise StoreNotFoundError(_("This field is required."), code="required")

    try:
        # Convert to int if it's a string representation of an integer
        if isinstance(store_id, str) and store_id.isdigit():
            store_id = int(store_id)

        store = Store.objects.get(pk=store_id)

        # Check if store is active (status == 'active')
        if store.status != "active":
            raise StoreNotFoundError(_("Store is not active."), code="inactive")

        return store

    except (Store.DoesNotExist, ValueError):
        raise StoreNotFoundError(_("Invalid store."), code="invalid")


class StoreScopedMixin:
    """
    Mixin for DRF viewsets that automatically resolves the current store
    from the request and makes it available as self.store.

    All store-scoped viewsets should inherit from this mixin first, then DRF classes.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to set self.store before any other processing.
        This ensures store is available for permissions and other methods.
        """
        # Set store before calling super().dispatch()
        self.store = get_store_from_request(request)
        return super().dispatch(request, *args, **kwargs)
