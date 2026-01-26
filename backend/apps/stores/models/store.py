"""
Store model for Digital Farmers CMS.

Multi-tenant store model for store-scoped data.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
import secrets

User = get_user_model()


class Store(models.Model):
    """Store model following DFCMS patterns with explicit store scoping"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    TYPE_CHOICES = [
        ('ecommerce', 'E-commerce'),
        ('blog', 'Blog'),
        ('portfolio', 'Portfolio'),
        ('corporate', 'Corporate'),
        ('other', 'Other'),
    ]
    
    # Core fields (from DFCMS)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Ownership (DFCMS compatibility)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_stores'
    )
    
    # Access & Security (from DFCMS)
    access_code = models.CharField(max_length=6, unique=True, editable=False)
    verification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    
    # Status & Type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    store_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ecommerce')
    
    # Enhanced Features
    domain = models.URLField(blank=True, null=True, unique=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='stores/favicons/', blank=True, null=True)
    
    # Dynamic Settings (JSON field for configs)
    settings = models.JSONField(default=dict, blank=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Bootstrap tracking fields
    bootstrap_completed = models.BooleanField(
        default=False,
        help_text="Indicates if bootstrap process has completed successfully"
    )
    bootstrap_phase = models.CharField(
        max_length=50,
        blank=True,
        help_text="Current phase of the bootstrap process"
    )
    bootstrap_error = models.TextField(
        blank=True,
        help_text="Any errors that occurred during bootstrap"
    )
    
    # Metafields support
    metafields = GenericRelation(
        'metafields.Metafield',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='store'
    )
    
    class Meta:
        db_table = 'stores_store'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['domain']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Generate access code and verification token for new stores
        if not self.pk:
            self.access_code = self._generate_access_code()
            self.verification_token = secrets.token_urlsafe(32)
        
        super().save(*args, **kwargs)
        
        # Bootstrap trigger for new stores
        if is_new:
            # from .services import StoreBootstrapService
            # StoreBootstrapService.bootstrap_store(self)
            pass
    
    def _generate_access_code(self):
        """Generate unique 6-digit access code"""
        while True:
            code = ''.join(secrets.choice('0123456789') for _ in range(6))
            if not Store.objects.filter(access_code=code).exists():
                return code
    
    def get_absolute_url(self):
        """Get store URL"""
        return f"/store/{self.slug}"
    
    def get_metafield(self, namespace, key):
        """Helper to get a metafield value"""
        from apps.metafields.services import MetafieldService
        return MetafieldService.get_metafield(
            self, 
            namespace=namespace, 
            key=key
        )
    
    def set_metafield(self, namespace, key, value):
        """Helper to set a metafield value"""
        from apps.metafields.services import MetafieldService
        return MetafieldService.set_metafield(
            self,
            namespace=namespace,
            key=key,
            value=value
        )
    
    def get_all_metafields(self):
        """Get all metafields as a dictionary"""
        from apps.metafields.services import MetafieldService
        metafields = {}
        for metafield in MetafieldService.get_metafields_for_object(self):
            key = f"{metafield.definition.namespace}.{metafield.definition.key}"
            metafields[key] = metafield.get_value()
        return metafields
