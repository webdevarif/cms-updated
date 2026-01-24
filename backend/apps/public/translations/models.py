"""
Translation models.
"""
from django.db import models


class Language(models.Model):
    """Supported languages in the system"""
    code = models.CharField(max_length=10, unique=True, help_text="ISO 639-1 code")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translations_language'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class TranslationKey(models.Model):
    """Translation keys with metadata"""
    key = models.CharField(max_length=255, unique=True, db_index=True)
    namespace = models.CharField(max_length=100, db_index=True, default='default')
    description = models.TextField(blank=True)
    
    CONTENT_TYPE_CHOICES = [
        ('plain', 'Plain Text'),
        ('html', 'HTML Content')
    ]
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='plain'
    )
    
    PLURAL_FORM_CHOICES = [
        ('none', 'Not pluralizable'),
        ('en', 'English (1 item/2 items)'),
        ('ar', 'Arabic (complex forms)')
    ]
    plural_form = models.CharField(
        max_length=10,
        choices=PLURAL_FORM_CHOICES,
        default='none'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translations_key'
        ordering = ['namespace', 'key']
    
    def __str__(self):
        return f"{self.namespace}.{self.key}"


class Translation(models.Model):
    """Actual translations"""
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    is_auto_translated = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translations_translation'
        unique_together = [['key', 'language', 'store']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.key.key} - {self.language.code}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_text = None
        
        if not is_new:
            old_instance = Translation.objects.get(pk=self.pk)
            old_text = old_instance.text
        
        super().save(*args, **kwargs)
        
        # Invalidate cache when translation is updated
        from .tasks import invalidate_translation_on_update
        invalidate_translation_on_update.delay(self.id)
        
        from apps.logs.tasks import log_event_async
        
        if is_new:
            log_event_async.delay({
                'event_type': 'create_translation_public_translations',
                'message': f"Translation created: {self.key.key} - {self.language.code}",
                'store_id': self.store.id if self.store else None,
                'object_id': self.id,
                'metadata': {
                    'key': self.key.key,
                    'namespace': self.key.namespace,
                    'language': self.language.code,
                    'is_auto_translated': self.is_auto_translated,
                    'needs_review': self.needs_review
                }
            })
        elif old_text != self.text:
            log_event_async.delay({
                'event_type': 'update_translation_public_translations',
                'message': f"Translation updated: {self.key.key} - {self.language.code}",
                'store_id': self.store.id if self.store else None,
                'object_id': self.id,
                'metadata': {
                    'key': self.key.key,
                    'namespace': self.key.namespace,
                    'language': self.language.code,
                    'is_auto_translated': self.is_auto_translated,
                    'needs_review': self.needs_review
                }
            })
