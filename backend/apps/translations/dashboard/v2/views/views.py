"""
Dashboard translations API views.
"""
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from ..models import Translation
from .serializers import TranslationDashboardSerializer


class TranslationDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard translations API - full admin CRUD on all translations + bulk import/export.
    Store owners can manage all translations across all stores they own.
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = TranslationDashboardSerializer

    def get_queryset(self):
        """Filter to owner's store translations"""
        return Translation.objects.filter(store__owner=self.request.user).select_related('language', 'translation_key', 'store')

    def perform_create(self, serializer):
        """Set store when creating translation"""
        serializer.save(store=self.request.store)

    @extend_schema(
        summary="List translations",
        description="Get all translations for owned stores"
    )
    def list(self, request, *args, **kwargs):
        """List translations"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create translation",
        description="Create new translation for store"
    )
    def create(self, request, *args, **kwargs):
        """Create translation"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update translation",
        description="Update existing translation"
    )
    def update(self, request, *args, **kwargs):
        """Update translation"""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete translation",
        description="Delete translation"
    )
    def destroy(self, request, *args, **kwargs):
        """Delete translation"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Bulk import translations from CSV/JSON"""
        import_format = request.data.get('format', 'json')
        translations_data = request.data.get('translations', [])

        if not translations_data:
            return Response(
                {'error': 'No translation data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        imported_count = 0
        errors = []

        for translation_data in translations_data:
            try:
                serializer = self.get_serializer(data=translation_data)
                if serializer.is_valid():
                    serializer.save()
                    imported_count += 1
                else:
                    errors.append({
                        'data': translation_data,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'data': translation_data,
                    'error': str(e)
                })

        return Response({
            'imported': imported_count,
            'errors': errors,
            'total_processed': len(translations_data)
        })

    @action(detail=False, methods=['get'])
    def bulk_export(self, request):
        """Export all translations as JSON"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'translations': serializer.data,
            'count': len(serializer.data),
            'exported_at': timezone.now().isoformat()
        })

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update translations"""
        updates = request.data.get('updates', [])

        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        errors = []

        for update_data in updates:
            translation_id = update_data.get('id')
            if not translation_id:
                errors.append({'error': 'Missing translation ID', 'data': update_data})
                continue

            try:
                translation = self.get_queryset().get(id=translation_id)
                serializer = self.get_serializer(translation, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_count += 1
                else:
                    errors.append({
                        'id': translation_id,
                        'errors': serializer.errors
                    })
            except Translation.DoesNotExist:
                errors.append({
                    'id': translation_id,
                    'error': 'Translation not found'
                })
            except Exception as e:
                errors.append({
                    'id': translation_id,
                    'error': str(e)
                })

        return Response({
            'updated': updated_count,
            'errors': errors,
            'total_processed': len(updates)
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete translations"""
        translation_ids = request.data.get('ids', [])

        if not translation_ids:
            return Response(
                {'error': 'No translation IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter to owner's translations only
        queryset = self.get_queryset().filter(id__in=translation_ids)
        deleted_count = queryset.count()
        queryset.delete()

        return Response({
            'deleted': deleted_count,
            'requested': len(translation_ids)
        })

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get translations analytics and statistics for the store with time-range filtering"""
        user = request.user
        if not user:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Parse time range parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        from datetime import datetime
        
        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                date_filter['created_at__gte'] = start_dt
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                date_filter['created_at__lte'] = end_dt
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            # Base queryset with date filtering and store ownership
            base_queryset = Translation.objects.filter(
                store__owner=user, **date_filter
            )

            # Translation counts by status and language
            total_translations = base_queryset.count()
            active_translations = base_queryset.filter(is_active=True).count()
            inactive_translations = base_queryset.filter(is_active=False).count()

            # Language distribution
            from django.db.models import Count
            languages = base_queryset.values('language__code', 'language__name').annotate(
                count=Count('id'),
                active_count=Count('id', filter=Q(is_active=True))
            ).order_by('-count')

            language_data = []
            for lang in languages:
                language_data.append({
                    'code': lang['language__code'],
                    'name': lang['language__name'],
                    'total_translations': lang['count'],
                    'active_translations': lang['active_count'],
                    'completion_rate': (lang['active_count'] / lang['count'] * 100) if lang['count'] > 0 else 0
                })

            # Translation key usage
            translation_keys = base_queryset.values('translation_key__key').annotate(
                total_translations=Count('id'),
                languages_covered=Count('language', distinct=True),
                completion_rate=Count('id', filter=Q(is_active=True)) * 100.0 / Count('id')
            ).order_by('-total_translations')[:20]

            key_data = []
            for key in translation_keys:
                key_data.append({
                    'key': key['translation_key__key'],
                    'total_translations': key['total_translations'],
                    'languages_covered': key['languages_covered'],
                    'completion_rate': float(key['completion_rate'])
                })

            # Store performance (translations per store)
            stores = base_queryset.values('store__name', 'store__id').annotate(
                total_translations=Count('id'),
                active_translations=Count('id', filter=Q(is_active=True)),
                languages=Count('language', distinct=True)
            ).order_by('-total_translations')

            store_data = []
            for store in stores:
                store_data.append({
                    'id': store['store__id'],
                    'name': store['store__name'],
                    'total_translations': store['total_translations'],
                    'active_translations': store['active_translations'],
                    'languages': store['languages']
                })

            # Missing translations (keys without translations in certain languages)
            # This would require more complex queries to identify gaps

            # Translation activity trends
            translation_trends = []
            if start_date and end_date:
                from django.db.models.functions import TruncDate
                daily_activity = base_queryset.annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(
                    created=Count('id'),
                    updated=Count('id', filter=Q(updated_at__date=F('created_at__date')))
                ).order_by('date')

                translation_trends = [{
                    'date': str(item['date']),
                    'translations_created': item['created'],
                    'translations_updated': item['updated']
                } for item in daily_activity]

            analytics_data = {
                'overview': {
                    'total_translations': total_translations,
                    'active_translations': active_translations,
                    'inactive_translations': inactive_translations,
                    'completion_rate': (active_translations / total_translations * 100) if total_translations > 0 else 0,
                    'total_languages': len(language_data),
                    'total_stores': len(store_data)
                },
                'languages': language_data,
                'translation_keys': key_data,
                'stores': store_data,
                'trends': {
                    'activity': translation_trends
                },
                'quality_metrics': {
                    'avg_translations_per_key': total_translations / len(key_data) if key_data else 0,
                    'most_translated_keys': key_data[:5] if key_data else [],
                    'least_translated_keys': key_data[-5:] if len(key_data) >= 5 else key_data
                },
                'time_range': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'has_date_filter': bool(start_date or end_date)
                }
            }

            return Response(analytics_data)

        except Exception as e:
            return Response(
                {'error': f'Analytics failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
