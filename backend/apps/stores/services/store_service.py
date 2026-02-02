"""
Services for stores module.
"""

import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.store import Store

# StoreSettings import removed - model doesn't exist

logger = logging.getLogger(__name__)


class StoreService:
    """Store business logic following DFCMS patterns"""

    @staticmethod
    @transaction.atomic
    def create_store(owner, store_data):
        """Create new store with settings and theme"""
        try:
            from ..models import Store, StoreSettings

            # Create store
            store = Store.objects.create(
                owner=owner,
                name=store_data["name"],
                slug=store_data.get("slug", ""),
                description=store_data.get("description", ""),
                store_type=store_data.get("store_type", "ecommerce"),
            )

            # Create default settings
            StoreSettings.objects.create(
                store=store, site_name=store.name, contact_email=owner.email
            )

            # Log store creation
            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="CONTENT_CREATE",
                event_name=f"Store created: {store.name}",
                properties={
                    "user": owner.id if owner else None,
                    "store": store.id,
                    "entity_type": "Store",
                    "entity_id": store.id,
                    "store_data": store_data,
                },
                user=owner,
                store=store,
            )

            return store

        except Exception as e:
            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="SYSTEM_ERROR",
                event_name=f"Failed to create store: {str(e)}",
                properties={
                    "user": owner.id if owner else None,
                    "level": "ERROR",
                    "error": str(e),
                    "store_data": store_data,
                },
                user=owner,
                store=None,
            )
            raise

    @staticmethod
    def update_store(store, update_data, user=None):
        """Update store with logging"""
        try:
            old_data = {
                "name": store.name,
                "status": store.status,
                "description": store.description,
            }

            for field, value in update_data.items():
                if hasattr(store, field):
                    setattr(store, field, value)

            store.save()

            # Log update
            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="CONTENT_UPDATE",
                event_name=f"Store updated: {store.name}",
                properties={
                    "user": user.id if user else None,
                    "store": store.id,
                    "entity_type": "Store",
                    "entity_id": store.id,
                    "old_data": old_data,
                    "new_data": update_data,
                },
                user=user,
                store=store,
            )

            return store

        except Exception as e:
            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="SYSTEM_ERROR",
                event_name=f"Failed to update store: {str(e)}",
                properties={
                    "user": user.id if user else None,
                    "level": "ERROR",
                    "error": str(e),
                    "old_data": old_data,
                    "new_data": update_data,
                },
                user=user,
                store=store,
            )
            raise

    @staticmethod
    def verify_store(store, token):
        """Verify store email"""
        if store.verification_token == token:
            store.status = "active"
            store.verification_token = None
            store.save()

            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="CONTENT_UPDATE",
                event_name=f"Store verified: {store.name}",
                properties={
                    "store": store.id,
                    "entity_type": "Store",
                    "entity_id": store.id,
                    "verification": True,
                },
                store=store,
            )

            return True
        return False

    @staticmethod
    def get_store_analytics(store, days=30):
        """Get store analytics data from analytics"""
        from apps.analytics.models.events import EventLog

        since = timezone.now() - timedelta(days=days)

        # Get analytics from analytics app
        page_views = EventLog.objects.filter(
            store=store, event_type="PAGE_VIEW", created_at__gte=since
        ).count()

        unique_visitors = (
            EventLog.objects.filter(store=store, event_type="PAGE_VIEW", created_at__gte=since)
            .values("session_id")
            .distinct()
            .count()
        )

        security_events = EventLog.objects.filter(
            store=store,
            event_type__in=["SECURITY_EVENT", "USER_AUTH"],
            created_at__gte=since,
        ).count()

        return {
            "page_views": page_views,
            "unique_visitors": unique_visitors,
            "security_events": security_events,
            "period_days": days,
        }


class StoreBootstrapService:
    """Store bootstrap service"""

    @staticmethod
    @transaction.atomic
    def bootstrap_store(store, actor=None):
        """
        Bootstrap a new store with all required components
        """
        try:
            logger.info(f"Starting bootstrap for store: {store.slug}")
            actor = actor or store.owner

            # Phase 1: Core store creation (already done)
            StoreBootstrapService._phase1_complete(store)

            # Phase 2: Content type initialization
            StoreBootstrapService._bootstrap_phase_2(store, actor)

            # Phase 3: Role and permission setup
            StoreBootstrapService._bootstrap_phase_3(store, actor)

            # Phase 4: Default configuration
            StoreBootstrapService._phase4_configuration(store)

            # Phase 5: Theme initialization
            StoreBootstrapService._phase5_theme(store)

            # Phase 6: Search index creation
            StoreBootstrapService._phase6_search_index(store)

            # Phase 7: Cache warming
            StoreBootstrapService._phase7_cache_warming(store)

            # Phase 8: Notification setup
            StoreBootstrapService._phase8_notifications(store)

            # Mark as complete
            store.bootstrap_completed = True
            store.bootstrap_phase = "completed"
            store.save(update_fields=["bootstrap_completed", "bootstrap_phase"])

            logger.info(f"Bootstrap complete for store: {store.slug}")

        except Exception as e:
            store.bootstrap_error = str(e)
            store.save(update_fields=["bootstrap_error"])
            logger.error(f"Bootstrap failed for store {store.slug}: {e}")
            raise

    @staticmethod
    def _phase1_complete(store):
        """Phase 1: Core store creation (already done)"""
        store.bootstrap_phase = "phase1_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 1 complete for store: {store.slug}")

    @staticmethod
    def _bootstrap_phase_2(store, actor):
        """Initialize content types and default pages"""
        logger.info(f"Starting phase 2 for store: {store.slug}")

        # Create required post types
        post_types = [
            {
                "name": "Page",
                "slug": "page",
                "description": "Static pages for the store",
                "is_system": True,
                "is_deletable": False,
            },
            {
                "name": "Blog",
                "slug": "blog",
                "description": "Blog posts for the store",
                "is_system": True,
                "is_deletable": False,
            },
            {
                "name": "Product",
                "slug": "product",
                "description": "Product catalog",
                "is_system": True,
                "is_deletable": False,
            },
        ]

        for post_type_data in post_types:
            from apps.posts.models import PostType

            PostType.objects.get_or_create(
                store=store,
                slug=post_type_data["slug"],
                defaults={
                    "name": post_type_data["name"],
                    "description": post_type_data["description"],
                    "is_system": post_type_data["is_system"],
                    "is_deletable": post_type_data["is_deletable"],
                    "created_by": actor,
                },
            )

        # Create default pages
        StoreBootstrapService._create_default_pages(store, actor)

        store.bootstrap_phase = "phase2_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 2 complete for store: {store.slug}")

    @staticmethod
    def _create_default_pages(store, actor):
        """Create default pages"""
        from apps.posts.models import Post, PostType

        page_type = PostType.objects.get(store=store, slug="page")

        pages = [
            {"title": "Home", "slug": "home", "content": "Welcome to your store!"},
            {"title": "About Us", "slug": "about", "content": "About our store"},
            {"title": "Contact", "slug": "contact", "content": "Contact us"},
        ]

        for page_data in pages:
            Post.objects.get_or_create(
                store=store,
                slug=page_data["slug"],
                defaults={
                    "title": page_data["title"],
                    "content": page_data["content"],
                    "post_type": page_type,
                    "is_published": True,
                    "created_by": actor,
                },
            )

    @staticmethod
    def _bootstrap_phase_3(store, actor):
        """Initialize roles and permissions"""
        logger.info(f"Starting phase 3 for store: {store.slug}")

        # Create default roles
        roles = [
            {
                "name": "Owner",
                "slug": "owner",
                "description": "Full access to all store features",
                "is_system": True,
                "permissions": ["*"],
            },
            {
                "name": "Admin",
                "slug": "admin",
                "description": "Administrative access to store",
                "is_system": True,
                "permissions": ["content.*", "ecommerce.*", "settings.*"],
            },
            {
                "name": "Manager",
                "slug": "manager",
                "description": "Manager access to store",
                "is_system": True,
                "permissions": [
                    "content.read",
                    "content.write",
                    "ecommerce.read",
                    "ecommerce.write",
                ],
            },
            {
                "name": "Staff",
                "slug": "staff",
                "description": "Staff access to store",
                "is_system": True,
                "permissions": ["content.read", "ecommerce.read"],
            },
            {
                "name": "Viewer",
                "slug": "viewer",
                "description": "Read-only access to store",
                "is_system": True,
                "permissions": ["content.read"],
            },
        ]

        owner_role = None

        for role_data in roles:
            from apps.accounts.models import Role

            role, created = Role.objects.get_or_create(
                store=store,
                slug=role_data["slug"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                    "is_system": role_data["is_system"],
                    "created_by": actor,
                },
            )

            if created and role_data.get("permissions"):
                role.permissions.set(role_data["permissions"])

            if role.slug == "owner":
                owner_role = role

        # Assign owner role to the actor
        if owner_role:
            from apps.accounts.models import StoreMember

            StoreMember.objects.get_or_create(
                store=store,
                user=actor,
                defaults={"role": owner_role, "is_active": True},
            )

        store.bootstrap_phase = "phase3_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 3 complete for store: {store.slug}")

    @staticmethod
    def _phase4_configuration(store):
        """Phase 4: Default configuration"""
        from apps.metafields.services import MetafieldService

        # Set default store configuration
        default_config = {
            "currency": "USD",
            "timezone": "UTC",
            "language": "en_US",
            "date_format": "MM/DD/YYYY",
            "time_format": "HH:mm",
            "tax_rate": "0.00",
            "shipping_free_threshold": "0",
        }

        for key, value in default_config.items():
            MetafieldService.set_metafield(instance=store, namespace="config", key=key, value=value)

        store.bootstrap_phase = "phase4_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 4 complete for store: {store.slug}")

    @staticmethod
    def _phase5_theme(store):
        """Phase 5: Theme initialization"""
        try:
            from apps.themes.services import ThemeService

            # Create default theme
            theme = ThemeService.create_theme(store, "Default Theme")

            # Activate the theme
            theme.activate()

            # Create default templates
            # TODO: Implement template creation in consolidated services
            # TemplateService.create_default_templates(theme)

        except Exception as e:
            logger.warning(f"Phase 5 skipped for store {store.slug}: {e}")

        store.bootstrap_phase = "phase5_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 5 complete for store: {store.slug}")

    @staticmethod
    def _phase6_search_index(store):
        """Phase 6: Search index creation - DISABLED"""
        # Search indexing removed - search app deleted
        logger.info(f"Phase 6 skipped for store {store.slug}: search app removed")

        store.bootstrap_phase = "phase6_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 6 complete for store: {store.slug}")

    @staticmethod
    def _phase7_cache_warming(store):
        """Phase 7: Cache warming - DISABLED"""
        # Cache warming removed to simplify cache infrastructure
        # Store will work normally without pre-warmed cache
        logger.info(f"Phase 7 skipped (cache warming disabled) for store: {store.slug}")

        store.bootstrap_phase = "phase7_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 7 complete for store: {store.slug}")

    @staticmethod
    def _phase8_notifications(store):
        """Phase 8: Notification setup"""
        try:
            from apps.notifications.models import NotificationPreference, NotificationTemplate

            # Create default notification templates
            templates = [
                {
                    "notification_type": "order.created",
                    "title_template": "Order Created",
                    "message_template": "Your order {{order_number}} has been created",
                    "email_subject_template": "Order Confirmation - {{order_number}}",
                    "email_body_template": "Thank you for your order!",
                },
                {
                    "notification_type": "user.registered",
                    "title_template": "Welcome to {{store_name}}",
                    "message_template": "Welcome to our store!",
                    "email_subject_template": "Welcome to {{store_name}}",
                    "email_body_template": "Thank you for registering!",
                },
            ]

            for template_data in templates:
                NotificationTemplate.objects.get_or_create(
                    store=store,
                    notification_type=template_data["notification_type"],
                    defaults=template_data,
                )

            # Create default notification preferences for owner
            notification_types = [
                "order.created",
                "order.shipped",
                "order.delivered",
                "user.registered",
                "form.submitted",
                "system.alert",
            ]

            for notification_type in notification_types:
                NotificationPreference.objects.get_or_create(
                    store=store,
                    user=store.owner,
                    notification_type=notification_type,
                    defaults={
                        "channel_preferences": {"email": True, "in_app": True},
                        "digest_enabled": False,
                    },
                )
        except Exception as e:
            logger.warning(f"Phase 8 skipped for store {store.slug}: {e}")

        store.bootstrap_phase = "phase8_complete"
        store.save(update_fields=["bootstrap_phase"])
        logger.info(f"Phase 8 complete for store: {store.slug}")

    @staticmethod
    def retry_bootstrap(store):
        """Retry bootstrap for a store"""
        if store.bootstrap_completed:
            logger.warning(f"Store {store.slug} already bootstrapped")
            return False

        # Clear error
        store.bootstrap_error = ""
        store.save(update_fields=["bootstrap_error"])

        # Retry bootstrap
        StoreBootstrapService.bootstrap_store(store)

        return True


class StoreAccessService:
    """Service for managing store access codes and verification"""

    @staticmethod
    def generate_access_code():
        """Generate unique 6-digit access code"""
        import secrets

        while True:
            code = "".join(secrets.choice("0123456789") for _ in range(6))
            if not Store.objects.filter(access_code=code).exists():
                return code

    @staticmethod
    def validate_access_code(code, user):
        """Validate access code and check user eligibility"""
        from django.conf import settings

        try:
            # Check if code exists and is unused
            store_request = Store.objects.get(access_code=code, status="pending")

            # Check if user already has active stores (limit)
            active_stores = Store.objects.filter(
                owner=user, status__in=["active", "pending"]
            ).count()

            if active_stores >= getattr(settings, "MAX_STORES_PER_USER", 5):
                raise ValidationError("User has reached maximum store limit")

            return store_request

        except Store.DoesNotExist:
            raise ValidationError("Invalid access code")

    @staticmethod
    def create_store_request(user, store_data, access_code):
        """Create store request with access code validation"""
        # Validate access code
        validated_request = StoreAccessService.validate_access_code(access_code, user)

        # Create store
        store = Store.objects.create(
            owner=user,
            name=store_data["name"],
            description=store_data.get("description", ""),
            store_type=store_data.get("store_type", "ecommerce"),
            access_code=validated_request.access_code,
            status="pending",
        )

        # Generate verification token
        import secrets

        store.verification_token = secrets.token_urlsafe(32)
        store.save()

        # Send verification email
        StoreAccessService.send_verification_email(store)

        return store

    @staticmethod
    def send_verification_email(store):
        """Send store verification email"""
        from apps.smtp.services.smtp_service import send_email
        from django.conf import settings

        verification_url = f"{settings.FRONTEND_URL}/verify-store/{store.verification_token}"

        send_email(
            store=store,
            to_email=store.owner.email,
            subject=f"Verify your {store.name} store",
            html_content=f"""
            <h2>Welcome to {store.name}!</h2>
            <p>Please verify your store by clicking the link below:</p>
            <a href="{verification_url}">Verify Store</a>
            <p>This link will expire in 7 days.</p>
            """,
            context={"store": store, "verification_url": verification_url},
            async_=True,
            user=store.owner,
        )

    @staticmethod
    def verify_store(token):
        """Verify store using token"""
        try:
            store = Store.objects.get(verification_token=token, status="pending")

            # Check token expiry (7 days)
            if store.created_at < timezone.now() - timedelta(days=7):
                raise ValidationError("Verification token has expired")

            # Activate store
            store.status = "active"
            store.verification_token = None
            store.save()

            # Complete onboarding
            StoreOnboardingService.complete_onboarding(store)

            # Log activation
            from apps.analytics.services.event_service import EventService

            EventService.log_event(
                event_type="STORE_VERIFIED",
                event_name=f"Store {store.name} verified and activated",
                properties={
                    "store": store.id,
                },
                store=store,
            )
            return store

        except Store.DoesNotExist:
            raise ValidationError("Invalid verification token")


class StoreOnboardingService:
    """Handle post-verification store onboarding"""

    @staticmethod
    def complete_onboarding(store):
        """Complete store onboarding after verification"""
        # Create default store settings
        StoreSettings.objects.get_or_create(
            store=store,
            defaults={
                "site_name": store.name,
                "contact_email": store.owner.email,
                "currency": "USD",
                "timezone": "UTC",
                "language": "en",
            },
        )

        # Create default theme association
        try:
            from apps.themes.models import Theme

            default_theme = Theme.objects.filter(is_default=True).first()
            if default_theme:
                store.theme = default_theme
                store.save()
        except Exception:
            # Themes app might not be available, skip theme association
            pass

        # Send welcome email
        StoreOnboardingService.send_welcome_email(store)

        # Log onboarding completion
        from apps.analytics.services.event_service import EventService

        EventService.log_event(
            event_type="STORE_ONBOARDED",
            event_name=f"Store {store.name} onboarding completed",
            properties={
                "store": store.id,
            },
            store=store,
        )

    @staticmethod
    def send_welcome_email(store):
        """Send welcome email after store activation"""
        from apps.smtp.services.smtp_service import send_email
        from django.conf import settings

        send_email(
            store=store,
            to_email=store.owner.email,
            subject=f"Welcome to {store.name}!",
            html_content=f"""
            <h2>Congratulations!</h2>
            <p>Your store <strong>{store.name}</strong> is now active.</p>
            <p>Get started by:</p>
            <ul>
                <li>Setting up your store settings</li>
                <li>Adding your first products</li>
                <li>Customizing your theme</li>
            </ul>
            <a href="{settings.FRONTEND_URL}/stores/{store.slug}/dashboard">Go to Dashboard</a>
            """,
            context={"store": store},
            async_=True,
            user=store.owner,
        )
