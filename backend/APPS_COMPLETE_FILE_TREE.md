# Backend Apps File Tree - FINAL UPDATED VERSION

This file contains the complete directory structure of the `backend/apps/` directory after all layered architecture cleanups and standardization.

```
apps/
Update accounts module structure to reflect current state after standardization
├── accounts/
│   ├── admin.py (3196 bytes)
│   ├── apps.py (300 bytes)
│   ├── migrations/
│   │   ├── 0001_initial.py (10539 bytes)
│   │   ├── 0002_migrate_dfcms_users.py (3409 bytes)
│   │   └── __init__.py (174 bytes)
│   ├── models/
│   │   ├── __init__.py (283 bytes)
│   │   ├── activity.py (1765 bytes)
│   │   ├── preferences.py (1628 bytes)
│   │   ├── role.py (1450 bytes)
│   │   ├── store_user.py (1718 bytes)
│   │   └── user.py (4521 bytes)
│   └── services/
│       ├── __init__.py (25 bytes)
│       └── account_service.py (70 bytes)
├── cache/
│   ├── __init__.py (25 bytes)
│   ├── admin.py (393 bytes)
│   ├── apps.py (1604 bytes)
│   ├── management/
│   │   ├── __init__.py (171 bytes)
│   │   └── commands/
│   │       ├── __init__.py (171 bytes)
│   │       ├── analyze_cache.py (1256 bytes)
│   │       ├── clear_cache.py (1688 bytes)
│   │       └── warm_cache.py (1441 bytes)
│   ├── models/
│   │   ├── __init__.py (62 bytes)
│   │   └── models.py (2274 bytes)
│   ├── monitoring.py (10515 bytes)
│   ├── services/
│   │   ├── __init__.py (30 bytes)
│   │   └── cache_service.py (7263 bytes)
│   ├── signals.py (7340 bytes)
│   ├── tasks.py (6696 bytes)
│   └── tests/
│       ├── __init__.py (39 bytes)
│       └── test_models.py (1135 bytes)
├── customer/
├── customer/
│   ├── __init__.py
│   ├── __pycache__/ (0 items)
│   ├── accounts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── ecommerce/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── entities/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── forms/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── giftcards/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── notifications/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── pages/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── posts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── stores/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── themes/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── webhooks/
│   │   └── v2/
│   │       ├── __init__.py
│   └── urls.py
│   └── webhooks/
│       └── v2/
│           ├── __init__.py (26 bytes)
│           ├── serializers.py (749 bytes)
│           ├── urls.py (421 bytes)
│           └── views.py (5793 bytes)
├── dashboard/
│   ├── __init__.py
│   ├── __pycache__/ (0 items)
│   ├── accounts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── ecommerce/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── forms/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── giftcards/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── mediafile/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   │       └── tests/
│   │           ├── __init__.py
│   │           ├── __pycache__/ (0 items)
│   │           └── test_dashboard_mediafile.py
│   ├── metafields/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── pages/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── posts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── smtp/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── stores/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── test/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── themes/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── webhooks/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── __pycache__/ (0 items)
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   └── urls.py
├── ecommerce/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   │   └── __pycache__/ (0 items)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   ├── cart.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── product.py
│   │   └── product_variant.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   └── ecommerce_service.py
│   └── tests/
│       ├── __init__.py
│       ├── __pycache__/ (0 items)
│       ├── test_api.py
│       ├── test_models.py
│       └── test_services.py
├── entities/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
├── forms/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── form.py
│   │   ├── form_field.py
│   │   ├── form_submission.py
│   │   └── form_template.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── form_service.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_models.py
│       └── test_services.py
├── giftcards/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── giftcards.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── giftcard_service.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       └── test_services.py
├── logs/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   ├── tasks.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   └── utils/
│       ├── __init__.py
│       └── log_utils.py
├── mediafile/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── exceptions.py
│   ├── management/
│   │   └── commands/
│   │       └── migrate_media.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── media_file.py
│   │   └── media_folder.py
│   ├── serializers.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── media_service.py
│   └── signals.py
├── metafields/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   └── models/
│       ├── __init__.py
│       └── metafield.py
├── notifications/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── notification.py
│   │   └── notification_template.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── notification_service.py
│   ├── signals.py
│   ├── tasks.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_models.py
│       └── test_services.py
├── pages/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── pages.py
│   ├── permissions.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── page_service.py
│   ├── signals.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_models.py
│       └── test_services.py
├── posts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── post_revision.py
│   │   ├── post_type.py
│   │   ├── taxonomy.py
│   │   └── term.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── post_service.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_models.py
│       └── test_services.py
├── public/
│   ├── __init__.py
│   ├── accounts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── ecommerce/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── forms/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── giftcards/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── metafields/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── pages/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── posts/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── search/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── stores/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── themes/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── translations/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── webhooks/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   └── urls.py
├── queue/
│   ├── __init__.py
│   ├── __pycache__/ (0 items)
│   ├── admin.py
│   ├── apps.py
│   ├── management/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── list_tasks.py
│   │       ├── purge_tasks.py
│   │       └── retry_failed_tasks.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   └── models.py
│   ├── services.py
│   ├── tasks.py
│   └── tests/
│       ├── __init__.py
│       ├── __pycache__/ (0 items)
├── search/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   ├── tasks.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_store_isolation.py
│   └── v2/
│       ├── __init__.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── smtp/
│   ├── __init__.py
│   ├── __pycache__/ (0 items)
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   └── models.py
│   ├── services.py
│   ├── tasks.py
│   └── tests/
│       ├── __init__.py
│       ├── __pycache__/ (0 items)
│       └── test_api.py
├── stores/
│   ├── __init__.py
│   ├── admin.py
│   ├── api.md
│   ├── apps.py
│   ├── management/
│   │   └── commands/
│   │       ├── bootstrap_store.py
│   │       └── migrate_stores.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── __pycache__/ (0 items)
│   │   ├── settings.py
│   │   └── store.py
│   ├── services.py
│   ├── signals.py
│   └── tests/
│       └── __init__.py
├── test/
│   ├── __init__.py
│   ├── __pycache__/ (0 items)
│   ├── admin.py
│   ├── apps.py
│   ├── fixtures/
│   │   ├── roles.py
│   │   ├── stores.py
│   │   └── users.py
│   ├── management/
│   │   └── commands/
│   │       ├── bootstrap_tests.py
│   │       ├── run_all_tests.py
│   │       └── run_full_api_tests.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── reports.py
│   ├── runners/
│   │   ├── app_runner.py
│   │   └── global_runner.py
│   ├── services.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_store_isolation.py
│   └── utils/
│       ├── __init__.py
│       ├── assertions.py
│       └── client.py
├── themes/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── README.md
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── color_scheme.py
│       ├── layout.py
│       ├── style_class.py
│       ├── template.py
│       ├── theme.py
│       └── typography.py
├── translations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   ├── tasks.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_integration.py
│   │   └── test_store_isolation.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── translation_parser.py
│   └── v2/
│       ├── __init__.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
└── webhooks/
    ├── __init__.py
    ├── __pycache__/ (0 items)
    ├── admin.py
    ├── apps.py
    ├── management/
    │   └── commands/
    │       ├── cleanup_webhooks.py
    │       └── retry_failed_deliveries.py
    ├── models/
    │   ├── __init__.py
    │   ├── __pycache__/ (0 items)
    │   └── models.py
    ├── services.py
    ├── signals.py
    ├── tasks.py
    └── tests/
        ├── __init__.py
        ├── __pycache__/ (0 items)
        └── test_services.py

---

## Summary

This file tree shows the complete structure of the `backend/apps/` directory after all layered architecture cleanups:

- **Root modules**: Core apps with shared components (models/, services/, admin.py, migrations/)
- **Layered structure**: public/, customer/, and dashboard/ layers with v2/ API folders
- **Infrastructure modules**: cache, queue, smtp, logs, search, translations
- **Content modules**: pages, posts, ecommerce, forms, giftcards, themes
- **Utility modules**: test, mediafile, webhooks, notifications, entities, stores, accounts

**Key changes from initial structure:**
- All `models.py` files moved to `models/` folders with proper `__init__.py` imports
- Root-level API tests moved to appropriate layered `v2/tests/` directories
- All stray interface folders (`serializers/`, `views/`, `urls/`, `v2/`) removed from root level
- Clean separation between shared components (root) and API interfaces (layered)

All files and folders are documented in their proper hierarchical structure.
