from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    verbose_name = "Analytics"

    def ready(self):
        from core.services.registry import ServiceRegistry

        ServiceRegistry.register_service(
            "analytics", "EventService", "apps.analytics.services.event_service"
        )
        pass  # Add signal imports or registrations here later
