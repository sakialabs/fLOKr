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
