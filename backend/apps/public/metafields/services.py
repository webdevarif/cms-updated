"""Services for metafields module."""
from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from datetime import date, datetime

class MetafieldService:
    """Core service for metafield operations"""
    
    # Cache timeout in seconds (1 hour)
    CACHE_TIMEOUT = 3600
    
    @classmethod
    def get_cache_key(cls, store_id, namespace=None, key=None):
        """Generate cache key for metafield definitions"""
        if namespace and key:
            return f'metafield_def:{store_id}:{namespace}:{key}'
        elif namespace:
            return f'metafield_defs:{store_id}:{namespace}'
        return f'metafield_defs:{store_id}'
    
    @classmethod
    def get_metafield_definition(cls, store, namespace, key):
        """Get a metafield definition by namespace and key with caching"""
        cache_key = cls.get_cache_key(store.id, namespace, key)
        definition = cache.get(cache_key)
        
        if definition is None:
            from .models import MetafieldDefinition
            try:
                definition = MetafieldDefinition.objects.get(
                    store=store,
                    namespace=namespace,
                    key=key
                )
                cache.set(cache_key, definition, cls.CACHE_TIMEOUT)
            except MetafieldDefinition.DoesNotExist:
                return None
                
        return definition
    
    @classmethod
    def get_metafield_definitions(cls, store, namespace=None):
        """Get all metafield definitions for a store (optionally filtered by namespace)"""
        cache_key = cls.get_cache_key(store.id, namespace or 'all')
        definitions = cache.get(cache_key)
        
        if definitions is None:
            from .models import MetafieldDefinition
            qs = MetafieldDefinition.objects.filter(store=store)
            if namespace:
                qs = qs.filter(namespace=namespace)
            definitions = list(qs)
            cache.set(cache_key, definitions, cls.CACHE_TIMEOUT)
            
        return definitions
    
    @classmethod
    def invalidate_definition_cache(cls, store, namespace=None, key=None):
        """Invalidate cache for metafield definitions"""
        if namespace and key:
            cache.delete(cls.get_cache_key(store.id, namespace, key))
        cache.delete(cls.get_cache_key(store.id, namespace))
        cache.delete(cls.get_cache_key(store.id))
    
    @classmethod
    def get_metafield(cls, instance, definition=None, namespace=None, key=None):
        """Get a metafield value for an instance"""
        from .models import Metafield
        
        if not definition and (namespace and key):
            definition = cls.get_metafield_definition(instance.store, namespace, key)
            if not definition:
                return None
        
        content_type = ContentType.objects.get_for_model(instance)
        return Metafield.objects.filter(
            store=instance.store,
            definition=definition,
            content_type=content_type,
            object_id=instance.id
        ).select_related('definition').first()
    
    @classmethod
    def _infer_type(cls, value):
        """Infer metafield type from Python type"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, (date, datetime)):
            return 'date'
        elif isinstance(value, dict):
            return 'json'
        return 'text'
    
    @classmethod
    def set_metafield(cls, instance, namespace, key, value, create_definition=True):
        """Set a metafield value for an instance"""
        from .models import Metafield, MetafieldDefinition
        
        # Get or create definition
        definition = cls.get_metafield_definition(instance.store, namespace, key)
        
        if not definition and create_definition:
            # Auto-create definition if it doesn't exist
            field_type = cls._infer_type(value)
            definition = MetafieldDefinition(
                store=instance.store,
                name=f"{namespace}.{key}",
                namespace=namespace,
                key=key,
                type=field_type,
                content_types=[ContentType.objects.get_for_model(instance).model]
            )
            definition.full_clean()
            definition.save()
            cls.invalidate_definition_cache(instance.store)
        
        if not definition:
            raise ValueError(f"Metafield definition not found: {namespace}.{key}")
            
        # Get or create metafield
        content_type = ContentType.objects.get_for_model(instance)
        metafield, created = Metafield.objects.get_or_create(
            store=instance.store,
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            defaults={'value_text': str(value)}  # Will be overridden
        )
        
        # Set and validate value
        metafield.set_value(value)
        metafield.full_clean()
        metafield.save()
        
        return metafield
    
    @classmethod
    def set_metafield_value(cls, store, key, value, namespace='config'):
        """Set a metafield value for a store"""
        from .models import MetafieldDefinition
        
        # Get or create definition
        definition = cls.get_metafield_definition(store, namespace, key)
        
        if not definition:
            # Auto-create definition if it doesn't exist
            field_type = cls._infer_type(value)
            definition = MetafieldDefinition(
                store=store,
                name=f"{namespace}.{key}",
                namespace=namespace,
                key=key,
                type=field_type,
                content_types=['stores.Store']
            )
            definition.full_clean()
            definition.save()
            cls.invalidate_definition_cache(store)
        
        # Create metafield for store
        store_content_type = ContentType.objects.get_for_model(store)
        
        from .models import Metafield
        metafield, created = Metafield.objects.get_or_create(
            store=store,
            definition=definition,
            content_type=store_content_type,
            object_id=store.id
        )
        
        # Set value
        metafield.set_value(value)
        metafield.full_clean()
        metafield.save()
        
        return metafield
    
    @classmethod
    @transaction.atomic
    def bulk_update_metafields(cls, instance, metafield_data, create_definitions=True):
        """Update multiple metafields for an instance"""
        from .models import Metafield, MetafieldDefinition
        
        content_type = ContentType.objects.get_for_model(instance)
        updated_metafields = []
        definitions_to_create = []
        
        # First pass: collect definitions to create
        if create_definitions:
            existing_defs = {
                (d.namespace, d.key): d 
                for d in cls.get_metafield_definitions(instance.store)
            }
            
            for namespace_key in metafield_data.keys():
                if '.' not in namespace_key:
                    continue
                    
                namespace, key = namespace_key.split('.', 1)
                cache_key = (namespace, key)
                
                if cache_key not in existing_defs:
                    value = metafield_data[namespace_key]
                    field_type = cls._infer_type(value)
                    
                    definition = MetafieldDefinition(
                        store=instance.store,
                        name=f"{namespace}.{key}",
                        namespace=namespace,
                        key=key,
                        type=field_type,
                        content_types=[content_type.model]
                    )
                    definitions_to_create.append(definition)
                    existing_defs[cache_key] = definition
            
            # Bulk create new definitions
            if definitions_to_create:
                MetafieldDefinition.objects.bulk_create(definitions_to_create)
                cls.invalidate_definition_cache(instance.store)
        
        # Second pass: update metafields
        for namespace_key, value in metafield_data.items():
            if '.' not in namespace_key:
                continue
                
            namespace, key = namespace_key.split('.', 1)
            
            # Get or create metafield
            metafield, created = Metafield.objects.get_or_create(
                store=instance.store,
                definition=existing_defs[(namespace, key)],
                content_type=content_type,
                object_id=instance.id
            )
            
            # Set and validate value
            metafield.set_value(value)
            metafield.full_clean()
            updated_metafields.append(metafield)
        
        # Bulk update all metafields
        if updated_metafields:
            Metafield.objects.bulk_update(
                updated_metafields,
                [f'value_{f}' for f in ['text', 'number', 'boolean', 'date', 'json']] + 
                ['value_media_id', 'updated_at']
            )
        
        return updated_metafields
    
    @classmethod
    def get_metafields_for_object(cls, instance, namespace=None):
        """Get all metafields for an object, optionally filtered by namespace"""
        from .models import Metafield
        
        content_type = ContentType.objects.get_for_model(instance)
        queryset = Metafield.objects.filter(
            store=instance.store,
            content_type=content_type,
            object_id=instance.id
        ).select_related('definition')
        
        if namespace:
            queryset = queryset.filter(definition__namespace=namespace)
        
        return queryset
    
    @classmethod
    def get_metafields_by_namespace(cls, store, namespace):
        """Get all metafield definitions for a namespace"""
        from .models import MetafieldDefinition
        return MetafieldDefinition.objects.filter(
            store=store,
            namespace=namespace
        )
