from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import InventoryItem
from .serializers import (
    InventoryItemSerializer,
    InventoryItemListSerializer,
    InventoryItemCreateSerializer
)
from users.permissions import IsStewardOrAdmin


class InventoryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Inventory Item management."""
    queryset = InventoryItem.objects.select_related('hub', 'donor').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'condition', 'status', 'hub']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'name', 'quantity_available']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryItemListSerializer
        elif self.action == 'create':
            return InventoryItemCreateSerializer
        return InventoryItemSerializer
    
    def get_queryset(self):
        """Filter out inactive items for non-stewards."""
        queryset = super().get_queryset()
        
        # Stewards and admins can see all items
        if self.request.user.role in ['steward', 'admin']:
            return queryset
        
        # Regular users only see active items with availability
        return queryset.filter(status='active', quantity_available__gt=0)
    
    def get_permissions(self):
        """Stewards can create/update/delete items."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStewardOrAdmin()]
        return [IsAuthenticated()]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('hub_id', str, description='Filter by hub ID'),
            OpenApiParameter('available_only', bool, description='Show only available items'),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with filters."""
        queryset = self.get_queryset()
        
        # Filter by hub
        hub_id = request.query_params.get('hub_id')
        if hub_id:
            queryset = queryset.filter(hub_id=hub_id)
        
        # Filter by availability
        available_only = request.query_params.get('available_only', 'true').lower() == 'true'
        if available_only:
            queryset = queryset.filter(quantity_available__gt=0)
        
        # Apply search
        search_query = request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_inactive(self, request, pk=None):
        """Mark item as inactive (stewards only)."""
        item = self.get_object()
        item.status = 'inactive'
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'}
                }
            }
        },
        responses={200: {
            'type': 'object',
            'properties': {
                'tags': {'type': 'array', 'items': {'type': 'string'}},
                'category': {'type': 'string'},
                'detailed_tags': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'tag': {'type': 'string'},
                            'confidence': {'type': 'number'}
                        }
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsStewardOrAdmin])
    def suggest_tags(self, request):
        """
        Get AI-powered tag and category suggestions for an image.
        Useful for previewing tags before creating an item.
        """
        try:
            from ori_ai.image_tagger import get_image_tagger
            import requests as req
            
            # Get image data
            image_data = None
            
            if 'image' in request.FILES:
                # Read uploaded file
                image_file = request.FILES['image']
                image_data = image_file.read()
            elif 'image_url' in request.data:
                # Download from URL
                image_url = request.data['image_url']
                response = req.get(image_url, timeout=5)
                response.raise_for_status()
                image_data = response.content
            else:
                return Response(
                    {'error': 'Either image file or image_url must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get tagger and generate suggestions
            tagger = get_image_tagger()
            tags, category = tagger.suggest_tags_and_category(image_data)
            detailed_tags = tagger.generate_tags(image_data, top_k=5)
            
            return Response({
                'tags': tags,
                'category': category,
                'detailed_tags': detailed_tags,
                'message': 'Tags generated successfully. You can edit these before creating the item.'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Tag suggestion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
