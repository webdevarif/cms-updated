"""
Tenant middleware for Digital Farmers CMS.

This middleware identifies the tenant from the request URL and sets it in the
thread local storage for the duration of the request.
"""

import re
from threading import local

from django.conf import settings
from django.http import Http404
from django.urls import resolve

# Thread local storage for the current request
_thread_locals = local()


def get_current_tenant():
    """
    Retrieve the current tenant from thread local storage.

    Returns:
        The current tenant object or None if not set.
    """
    return getattr(_thread_locals, "tenant", None)


class TenantMiddleware:
    """
    Middleware to handle multi-tenancy based on URL path.

    The tenant is identified from the URL path in the format:
    /store/<store_slug>/...

    The store_slug is used to identify the tenant and is stored in thread local
    storage for the duration of the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Compile the store URL pattern for better performance
        self.store_url_pattern = re.compile(r"^/store/(?P<store_slug>[^/]+)")

    def __call__(self, request):
        # Default to no tenant
        _thread_locals.tenant = None

        # Check if the path starts with /store/
        match = self.store_url_pattern.match(request.path_info)
        if match:
            store_slug = match.group("store_slug")
            try:
                # Import here to avoid circular imports
                from stores.models import Store

                # Get the store/tenant
                store = Store.objects.get(slug=store_slug, is_active=True)
                _thread_locals.tenant = store

                # Add store to request for easy access in views
                request.tenant = store

            except Store.DoesNotExist:
                # Store not found, return 404
                raise Http404(f"Store '{store_slug}' does not exist or is not active.")

        # Call the next middleware/view
        response = self.get_response(request)

        # Clean up thread local storage
        if hasattr(_thread_locals, "tenant"):
            del _thread_locals.tenant

        return response
