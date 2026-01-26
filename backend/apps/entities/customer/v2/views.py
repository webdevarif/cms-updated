"""
Customer entities views - authenticated interface for entity interactions.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.contenttypes.models import ContentType

from apps.entities.models import EntityAction, EntityInteraction
from .serializers import CustomerEntityActionSerializer, CustomerEntityInteractionSerializer, CustomerEntityInteractionCreateSerializer


class CustomerEntityActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer entity actions API - authenticated access to entity actions.
    
    Provides:
    - List available entity actions
    - Get entity action details
    - View own interactions
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        return CustomerEntityActionSerializer
    
    def get_queryset(self):
        """Filter to active actions for the user's store."""
        queryset = EntityAction.objects.filter(
            is_active=True
        ).select_related('store')
        
        store = getattr(self.request, 'store', None)
        if store:
            queryset = queryset.filter(store=store)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def my_interactions(self, request, pk=None):
        """
        Get current user's interactions for this entity action.
        
        Returns:
            User's interactions for this action
        """
        entity_action = self.get_object()
        
        interactions = EntityInteraction.objects.filter(
            action=entity_action,
            user=request.user,
            is_active=True
        ).select_related('content_type')
        
        serializer = CustomerEntityInteractionSerializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def interact(self, request, pk=None):
        """
        Create or update an interaction with this entity action.
        
        Args:
            content_type: Content type ID
            object_id: Object ID
            value: Interaction value (optional)
            rating: Rating value (optional)
            
        Returns:
            Created or updated interaction
        """
        entity_action = self.get_object()
        
        # Check if action allows user interaction
        if not entity_action.is_public and not request.user.is_staff:
            return Response(
                {'error': 'This action is not available for users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CustomerEntityInteractionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            store = getattr(request, 'store', None)
            if not store:
                return Response(
                    {'error': 'Store not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create interaction
            interaction, created = EntityInteraction.objects.get_or_create(
                store=store,
                action=entity_action,
                user=request.user,
                content_type_id=serializer.validated_data['content_type'],
                object_id=serializer.validated_data['object_id'],
                defaults={
                    'value': serializer.validated_data.get('value', {}),
                    'rating': serializer.validated_data.get('rating'),
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            
            if not created:
                # Update existing interaction
                if 'value' in serializer.validated_data:
                    interaction.value = serializer.validated_data['value']
                if 'rating' in serializer.validated_data:
                    interaction.rating = serializer.validated_data['rating']
                interaction.is_active = True
                interaction.save()
            
            return Response(
                CustomerEntityInteractionSerializer(interaction).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def remove_interaction(self, request, pk=None):
        """
        Remove user's interaction with this entity action.
        
        Args:
            content_type: Content type ID
            object_id: Object ID
            
        Returns:
            Success message
        """
        entity_action = self.get_object()
        
        content_type_id = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            store = getattr(request, 'store', None)
            if not store:
                return Response(
                    {'error': 'Store not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            interaction = EntityInteraction.objects.get(
                store=store,
                action=entity_action,
                user=request.user,
                content_type_id=content_type_id,
                object_id=object_id
            )
            
            interaction.is_active = False
            interaction.save()
            
            return Response(
                {'message': 'Interaction removed successfully'},
                status=status.HTTP_200_OK
            )
            
        except EntityInteraction.DoesNotExist:
            return Response(
                {'error': 'Interaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CustomerEntityInteractionViewSet(viewsets.ModelViewSet):
    """
    Customer entity interactions API - authenticated access to own interactions.
    
    Provides:
    - View own interactions
    - Create interactions
    - Update interactions
    - Delete interactions
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['action__name', 'content_type__model']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CustomerEntityInteractionCreateSerializer
        return CustomerEntityInteractionSerializer
    
    def get_queryset(self):
        """Filter to user's own interactions."""
        queryset = EntityInteraction.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('action', 'content_type')
        
        store = getattr(self.request, 'store', None)
        if store:
            queryset = queryset.filter(store=store)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create interaction with user and store."""
        store = getattr(self.request, 'store', None)
        if store:
            serializer.save(
                user=self.request.user,
                store=store,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
    
    @action(detail=False, methods=['get'])
    def by_content(self, request):
        """
        Get user's interactions by content type and object ID.
        
        Args:
            content_type: Content type ID
            object_id: Object ID
            
        Returns:
            User's interactions for the specified content
        """
        content_type_id = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        interactions = self.get_queryset().filter(
            content_type_id=content_type_id,
            object_id=object_id
        )
        
        serializer = self.get_serializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary of user's interactions.
        
        Returns:
            Summary of user's interactions by action type
        """
        queryset = self.get_queryset()
        
        summary = {}
        for interaction in queryset:
            action_slug = interaction.action.slug
            if action_slug not in summary:
                summary[action_slug] = {
                    'name': interaction.action.name,
                    'action_type': interaction.action.action_type,
                    'count': 0,
                    'total_rating': 0,
                    'average_rating': 0
                }
            
            summary[action_slug]['count'] += 1
            
            if interaction.rating:
                summary[action_slug]['total_rating'] += interaction.rating
                summary[action_slug]['average_rating'] = (
                    summary[action_slug]['total_rating'] /
                    summary[action_slug]['count']
                )
        
        return Response(summary)
