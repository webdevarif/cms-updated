"""
Role model for Digital Farmers CMS.

Defines store-specific user roles and permissions.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    """Store-specific user roles with permissions"""
    ROLE_CHOICES = [
        ('owner', _('Owner')),
        ('admin', _('Admin')),
        ('manager', _('Manager')),
        ('staff', _('Staff')),
        ('customer', _('Customer')),
    ]
    
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name=_('store')
    )
    name = models.CharField(_('name'), max_length=20, choices=ROLE_CHOICES)
    permissions = models.JSONField(_('permissions'), default=dict)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'accounts_role'
        unique_together = [['store', 'name']]
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['store', 'name']
        indexes = [
            models.Index(fields=['store', 'name']),
            models.Index(fields=['store', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_name_display()} ({self.store.name})"
