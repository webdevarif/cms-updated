"""
URL configuration for the core module.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

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
    # Ecommerce APIs - migrated to internal layered structure
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
    # Cache API - TODO: Implement cache module
    # path('v2/api/cache/', include('apps.cache.v2.urls', namespace='cache_v2')),
    # Queue API - TODO: Implement task_queue module
    # path('v2/api/queue/', include('apps.task_queue.v2.urls', namespace='queue_v2')),
    # Translations API - migrated to internal layered structure
    path("v2/api/translations/", include("apps.translations.urls", namespace="translations_v2")),
    # Webhooks API - migrated to internal layered structure
    path("v2/api/webhooks/", include("apps.webhooks.urls", namespace="webhooks_v2")),
    # Test API - commented out until v2 structure is created
    # path('v2/api/test/', include('apps.test.v2.urls', namespace='test_v2')),
    # API Schema - drf-spectacular OpenAPI documentation
    path("api/schema/", include("drf_spectacular.urls")),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
