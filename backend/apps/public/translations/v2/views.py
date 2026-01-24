"""
API views for translations module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from core.permissions import IsStoreOwner
from ..models import Language, TranslationKey, Translation
from ..services import TranslationService
from .serializers import LanguageSerializer, TranslationKeySerializer, TranslationSerializer
from ..tasks import warm_store_translations, clear_translation_cache


class TranslationViewSet(viewsets.ModelViewSet):
    """
    Translation management endpoints
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    
    def get_queryset(self):
        return super().get_queryset().filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Translation",
        description="Get a specific translation",
        responses={200: TranslationSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Translation",
        description="Create a new translation",
        request=TranslationSerializer,
        responses={201: TranslationSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Translation",
        description="Update an existing translation",
        request=TranslationSerializer,
        responses={200: TranslationSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Translation",
        description="Delete a translation",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get Translation by Key",
        description="Get translation by key and language",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Get translation by key and language"""
        key = request.query_params.get('key')
        language_code = request.query_params.get('language', 'en')
        
        if not key:
            return Response(
                {'error': 'Key parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translation = TranslationService.get_translation(key, language_code, request.store)
        
        return Response({
            'key': key,
            'language': language_code,
            'translation': translation,
            'store_id': request.store.id if request.store else None
        })
    
    @extend_schema(
        summary="Bulk Create Translations",
        description="Create multiple translations at once",
        request=TranslationSerializer(many=True),
        responses={201: TranslationSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create translations"""
        translations_data = request.data
        
        if not isinstance(translations_data, list):
            return Response(
                {'error': 'Data must be a list of translation objects'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = TranslationService.bulk_create_translations(translations_data, request.store)
        
        serializer = TranslationSerializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Warm Cache",
        description="Warm translation cache for store",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def warm_cache(self, request):
        """Warm translation cache for the store"""
        if request.store:
            task = warm_store_translations.delay(request.store.id)
            return Response({
                'message': 'Cache warming started',
                'task_id': task.id
            })
        else:
            return Response(
                {'error': 'Store context required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Clear Cache",
        description="Clear translation cache",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """Clear translation cache"""
        store_id = request.store.id if request.store else None
        language_code = request.query_params.get('language')
        
        task = clear_translation_cache.delay(store_id, language_code)
        return Response({
            'message': 'Cache clearing started',
            'task_id': task.id
        })


class LanguageViewSet(viewsets.ModelViewSet):
    """
    Language management endpoints
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    
    @extend_schema(
        summary="Get Languages",
        description="List all available languages",
        responses={200: LanguageSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Language",
        description="Create a new language",
        request=LanguageSerializer,
        responses={201: LanguageSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Language",
        description="Update an existing language",
        request=LanguageSerializer,
        responses={200: LanguageSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Language",
        description="Delete a language",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TranslationKeyViewSet(viewsets.ModelViewSet):
    """
    Translation key management endpoints
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    queryset = TranslationKey.objects.all()
    serializer_class = TranslationKeySerializer
    
    def get_queryset(self):
        return super().get_queryset()
    
    @extend_schema(
        summary="Get Translation Keys",
        description="List all translation keys",
        responses={200: TranslationKeySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Translation Key",
        description="Create a new translation key",
        request=TranslationKeySerializer,
        responses={201: TranslationKeySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Translation Key",
        description="Update an existing translation key",
        request=TranslationKeySerializer,
        responses={200: TranslationKeySerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Translation Key",
        description="Delete a translation key",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
