"""
Views for customer entities API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.contenttypes.models import ContentType

from core.viewsets import TenantViewSet
from core.permissions import IsStoreUser
from apps.customer.entities.v2.serializers import EntityActionSerializer, EntityInteractionSerializer
from apps.entities.services import EntityService


class CustomerEntityViewSet(TenantViewSet):
    """
    Customer entity interaction endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    @extend_schema(
        summary="Toggle Entity Action",
        request=EntityActionSerializer,
        responses={200: EntityInteractionSerializer}
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle an entity action (like/unlike, etc.)"""
        serializer = EntityActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        content_type = ContentType.objects.get(
            model=serializer.validated_data['content_type']
        )
        model_class = content_type.model_class()
        content_object = model_class.objects.get(
            id=serializer.validated_data['object_id']
        )
        
        result = EntityService.toggle_action(
            user=request.user,
            content_object=content_object,
            action_slug=serializer.validated_data['action_slug'],
            store=request.store
        )
        
        return Response(result)
    
    @extend_schema(
        summary="Get Entity Stats",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get interaction statistics for an object"""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        action_slug = request.query_params.get('action_slug')
        
        if not all([content_type, object_id]):
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_type_obj = ContentType.objects.get(model=content_type)
        model_class = content_type_obj.model_class()
        content_object = model_class.objects.get(id=object_id)
        
        count = EntityService.get_interaction_count(
            content_object=content_object,
            action_slug=action_slug,
            store=request.store
        )
        
        user_interactions = EntityService.get_user_interactions(
            user=request.user,
            content_object=content_object,
            store=request.store
        )
        
        return Response({
            'count': count,
            'user_interactions': EntityInteractionSerializer(
                user_interactions, many=True
            ).data
        })
