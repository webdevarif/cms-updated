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
