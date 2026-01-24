"""
URL configuration for the core module.
"""
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
    # Admin
    path('admin/', include('core.urls.admin')),
    
    # V2 API URLs
    path('', include('core.urls.v2')),
    
    # Public API
    path('v2/api/public/accounts/', 
         include('apps.public.accounts.v2.urls', namespace='public_accounts_v2')),
    
    # Customer API
    path('v2/api/customer/accounts/',
         include('apps.customer.accounts.v2.urls', namespace='customer_accounts_v2')),
    
    # Dashboard API
    path('v2/api/dashboard/accounts/',
         include('apps.dashboard.accounts.v2.urls', namespace='dashboard_accounts_v2')),
    
    # Logs API
    path('v2/api/logs/', include('apps.logs.v2.urls', namespace='logs_v2')),
    
    # SMTP API
    path('v2/api/smtp/', include('apps.smtp.v2.urls', namespace='smtp_v2')),
    
    # Stores API
    path('v2/api/stores/', include('apps.stores.v2.urls', namespace='stores_v2')),
    
    # Media API
    path('v2/api/media/', include('apps.mediafile.v2.urls', namespace='mediafile_v2')),
    
    # Posts API
    path('v2/api/posts/', include('apps.posts.v2.urls', namespace='posts_v2')),
    
    # Notifications API
    path('v2/api/notifications/', include('apps.notifications.v2.urls', namespace='notifications_v2')),
    
    # Entities API
    path('v2/api/entities/', include('apps.entities.v2.urls', namespace='entities_v2')),
    
    # Ecommerce Public API
    path('v2/api/ecommerce/', include('apps.public.ecommerce.v2.urls', namespace='ecommerce_v2')),
    
    # Ecommerce Customer API
    path('v2/api/customer/ecommerce/', include('apps.customer.ecommerce.v2.urls', namespace='customer_ecommerce_v2')),
    
    # Ecommerce Dashboard API
    path('v2/api/dashboard/ecommerce/', include('apps.dashboard.ecommerce.v2.urls', namespace='dashboard_ecommerce_v2')),
    
    # Gift Cards API
    path('v2/api/gift-cards/', include('apps.public.giftcards.v2.urls', namespace='giftcards_v2')),
    
    # Metafields API
    path('v2/api/metafields/', include('apps.public.metafields.v2.urls', namespace='metafields_v2')),
    
    # Forms API
    path('v2/api/forms/', include('apps.public.forms.v2.urls', namespace='forms_v2')),
    
    # Search API
    path('v2/api/search/', include('apps.public.search.v2.urls', namespace='search_v2')),
    
    # Cache API - TODO: Implement cache module
    # path('v2/api/cache/', include('apps.public.cache.v2.urls', namespace='cache_v2')),
    
    # Queue API - TODO: Implement task_queue module  
    # path('v2/api/queue/', include('apps.public.task_queue.v2.urls', namespace='queue_v2')),
    
    # Translations API
    path('v2/api/translations/', include('apps.public.translations.v2.urls', namespace='translations_v2')),
    
    # Webhooks API
    path('v2/api/webhooks/', include('apps.webhooks.v2.urls', namespace='webhooks_v2')),
    
    # Test API
    path('v2/api/test/', include('apps.test.v2.urls', namespace='test_v2')),
    
    # API Schema (commented out until drf-spectacular is properly configured)
    # path('api/schema/', include('drf_spectacular.urls')),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
