"""
Core views for Digital Farmers CMS.
"""

from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render


def api_root(request):
    """API root endpoint"""
    return JsonResponse(
        {
            "message": "Digital Farmers CMS API",
            "version": "v2",
            "endpoints": {
                "admin": "/admin/",
                "accounts": "/v2/api/accounts/",
                "stores": "/v2/api/stores/",
                "forms": "/v2/api/forms/",
                "posts": "/v2/api/posts/",
                "themes": "/v2/api/themes/",
                "translations": "/v2/api/translations/",
                "webhooks": "/v2/api/webhooks/",
            },
        }
    )


def bad_request(request, exception):
    return HttpResponseBadRequest()


def permission_denied(request, exception):
    return HttpResponseForbidden()


def page_not_found(request, exception):
    return HttpResponseNotFound()


def server_error(request):
    return HttpResponseServerError()
