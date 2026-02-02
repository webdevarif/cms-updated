"""
Store settings model.
"""

from django.db import models


class StoreSettings(models.Model):
    """Store-specific settings with explicit store relationship"""

    store = models.OneToOneField(
        "stores.Store", on_delete=models.CASCADE, related_name="store_settings"
    )

    # General Settings
    site_name = models.CharField(max_length=255, default="My Store")
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Currency & Locale
    currency = models.CharField(max_length=3, default="USD")
    timezone = models.CharField(max_length=50, default="UTC")
    language = models.CharField(max_length=10, default="en")

    # E-commerce Settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    shipping_enabled = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Media References
    logo = models.ForeignKey(
        "mediafile.MediaFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="store_logos",
        help_text="Store logo image",
    )
    favicon = models.ForeignKey(
        "mediafile.MediaFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="store_favicons",
        help_text="Store favicon image",
    )

    # Advanced Settings (JSON for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stores_settings"

    def __str__(self):
        return f"{self.store.name} Settings"

    def set_logo_from_upload(self, uploaded_file, uploaded_by=None):
        """Set store logo using MediaService upload"""
        from apps.mediafile.services.media_service import MediaService

        media_service = MediaService()
        media_file = media_service.upload_from_request(
            store=self.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name="brand_assets",
            alt_text=f"{self.store.name} logo",
            description=f"Store logo for {self.store.name}",
        )

        self.logo = media_file
        self.save(update_fields=["logo"])
        return media_file

    def set_favicon_from_upload(self, uploaded_file, uploaded_by=None):
        """Set store favicon using MediaService upload"""
        from apps.mediafile.services.media_service import MediaService

        media_service = MediaService()
        media_file = media_service.upload_from_request(
            store=self.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name="brand_assets",
            alt_text=f"{self.store.name} favicon",
            description=f"Store favicon for {self.store.name}",
        )

        self.favicon = media_file
        self.save(update_fields=["favicon"])
        return media_file
