"""
URL configuration for the core module.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView


def schema_view(request):
    """Lazy-loaded schema view to avoid import-time settings access"""
    from drf_spectacular.views import SpectacularAPIView

    view = SpectacularAPIView.as_view()
    return view(request)


def swagger_view(request):
    """Lazy-loaded swagger view to avoid import-time settings access"""
    from drf_spectacular.views import SpectacularSwaggerView

    view = SpectacularSwaggerView.as_view(url="/api/schema/")
    return view(request)


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

app_name = "core"

urlpatterns = [
    # Admin
    path("admin/", include("core.urls.admin")),
    # Django Debug Toolbar (only in development)
    # path('__debug__/', include('debug_toolbar.urls')),
    # V2 API URLs
    path("", include("core.urls.v2")),
    # Public API
    # path('v2/api/public/accounts/',
    #      include('apps.accounts.v2.urls', namespace='public_accounts_v2')),
    # Customer API
    # path('v2/api/customer/accounts/',
    #      include('apps.accounts.v2.urls', namespace='customer_accounts_v2')),
    # Dashboard API
    # path('v2/api/dashboard/accounts/',
    #      include('apps.accounts.v2.urls', namespace='dashboard_accounts_v2')),
    # Accounts API - migrated to internal layered structure
    path("v2/api/accounts/", include("apps.accounts.urls", namespace="accounts_v2")),
    # Stores API - migrated to internal layered structure
    path("v2/api/stores/", include("apps.stores.urls", namespace="stores_v2")),
    # Notifications API - migrated to internal layered structure
    path("v2/api/notifications/", include("apps.notifications.urls", namespace="notifications_v2")),
    # Entities API - migrated to internal layered structure
    path("v2/api/entities/", include("apps.entities.urls", namespace="entities_v2")),
    # E-commerce APIs - migrated to internal layered structure
    path("v2/api/ecommerce/", include("apps.ecommerce.urls", namespace="ecommerce_v2")),
    # Gift Cards API - migrated to internal layered structure
    path("v2/api/gift-cards/", include("apps.giftcards.urls", namespace="giftcards_v2")),
    # Posts API - migrated to internal layered structure
    path("v2/api/posts/", include("apps.posts.urls", namespace="posts_v2")),
    # Metafields API - migrated to internal layered structure
    path("v2/api/metafields/", include("apps.metafields.urls", namespace="metafields_v2")),
    # Forms API - migrated to internal layered structure
    path("v2/api/forms/", include("apps.forms.urls", namespace="forms_v2")),
    # Logs API - migrated to internal layered structure
    path("v2/api/logs/", include("apps.logs.urls", namespace="logs_v2")),
    # Themes API - migrated to internal layered structure
    path("v2/api/themes/", include("apps.themes.urls", namespace="themes_v2")),
    # Cache API - Simple cache management views
    path(
        "v2/api/cache/stats/", lambda request: (lambda: None)(), name="cache_stats"
    ),  # TODO: Add cache views
    path(
        "v2/api/cache/clear/", lambda request: (lambda: None)(), name="clear_cache"
    ),  # TODO: Add cache views
    path(
        "v2/api/cache/warm/", lambda request: (lambda: None)(), name="warm_cache"
    ),  # TODO: Add cache views
    # Queue API - TODO: Implement task_queue module
    # path('v2/api/queue/', include('apps.task_queue.v2.urls', namespace='queue_v2')),
    # Translations API - migrated to internal layered structure
    path("v2/api/translations/", include("apps.translations.urls", namespace="translations_v2")),
    # Webhooks API - migrated to internal layered structure
    path("v2/api/webhooks/", include("apps.webhooks.urls", namespace="webhooks_v2")),
    # Test API - commented out until v2 structure is created
    # path('v2/api/test/', include('apps.test.v2.urls', namespace='test_v2')),
    # API Schema - drf-spectacular OpenAPI documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI - Redoc documentation
    path("api/docs/", SpectacularSwaggerView.as_view(url="/api/schema/"), name="swagger-ui"),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
