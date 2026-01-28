"""
Core views for Digital Farmers CMS.
"""
from django.http import JsonResponse


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
