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
    
    def perform_create(self, serializer):
        """Create item and award reputation for donations."""
        item = serializer.save()
        
        # If this is a donation (has a donor), award reputation
        if item.donor:
            from community.reputation_service import ReputationService
            ReputationService.award_points(item.donor, 'donate_item')
    
    @extend_schema(
        parameters=[
            OpenApiParameter('hub_id', str, description='Filter by hub ID'),
            OpenApiParameter('available_only', bool, description='Show only available items'),
            OpenApiParameter('prioritize_user_hub', bool, description='Prioritize items from user\'s assigned hub'),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search with filters and hub-prioritized ranking.
        Items from user's assigned hub appear first.
        """
        from django.db.models import Case, When, Value, IntegerField
        
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
        
        # Hub-prioritized ranking (user's hub items first)
        prioritize = request.query_params.get('prioritize_user_hub', 'true').lower() == 'true'
        if prioritize and request.user.assigned_hub:
            user_hub_id = request.user.assigned_hub.id
            queryset = queryset.annotate(
                hub_priority=Case(
                    When(hub_id=user_hub_id, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            ).order_by('hub_priority', '-created_at')
        
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsStewardOrAdmin])
    def unflag(self, request, pk=None):
        """
        Unflag an item after resolving incident reports (stewards only).
        Requires 'resolution_notes' in request data.
        """
        from community.incident_service import IncidentService
        
        item = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        if not resolution_notes:
            return Response(
                {'error': 'resolution_notes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not item.is_flagged:
            return Response(
                {'error': 'Item is not flagged'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        IncidentService.unflag_item(item, request.user, resolution_notes)
        
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
    @action(detail=True, methods=['post'], permission_classes=[IsStewardOrAdmin])
    def initiate_transfer(self, request, pk=None):
        """
        Initiate transfer of items to another hub (stewards only).
        Requires: to_hub_id, quantity, reason
        """
        from .transfer_service import InventoryTransferService
        from hubs.models import Hub
        
        item = self.get_object()
        to_hub_id = request.data.get('to_hub_id')
        quantity = request.data.get('quantity', 1)
        reason = request.data.get('reason', '')
        
        if not to_hub_id:
            return Response(
                {'error': 'to_hub_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            to_hub = Hub.objects.get(pk=to_hub_id)
        except Hub.DoesNotExist:
            return Response(
                {'error': 'Destination hub not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            transfer = InventoryTransferService.initiate_transfer(
                item=item,
                from_hub=item.hub,
                to_hub=to_hub,
                quantity=int(quantity),
                initiated_by=request.user,
                reason=reason
            )
            
            return Response({
                'message': 'Transfer initiated successfully',
                'transfer_id': str(transfer.id),
                'status': transfer.status
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsStewardOrAdmin])
    def transfers(self, request):
        """
        Get all transfers for user's hub (incoming and outgoing).
        Stewards see transfers for their hub, admins see all.
        """
        from .transfer_service import InventoryTransferService
        from .models import InventoryTransfer
        
        if request.user.role == 'admin':
            # Admins see all transfers
            transfers = InventoryTransfer.objects.all()
        elif request.user.assigned_hub:
            # Stewards see transfers for their hub
            hub = request.user.assigned_hub
            transfers_data = InventoryTransferService.get_hub_transfers(hub)
            
            # Combine and serialize
            from .serializers import InventoryTransferSerializer
            incoming_data = InventoryTransferSerializer(transfers_data['incoming'], many=True).data
            outgoing_data = InventoryTransferSerializer(transfers_data['outgoing'], many=True).data
            
            return Response({
                'incoming': incoming_data,
                'outgoing': outgoing_data
            })
        else:
            return Response(
                {'error': 'No hub assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Admin response
        from .serializers import InventoryTransferSerializer
        serializer = InventoryTransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsStewardOrAdmin],
            url_path='transfers/(?P<transfer_id>[^/.]+)/approve')
    def approve_transfer(self, request, transfer_id=None):
        """Approve a pending transfer (stewards at destination hub)."""
        from .transfer_service import InventoryTransferService
        from .models import InventoryTransfer
        
        try:
            transfer = InventoryTransfer.objects.get(pk=transfer_id)
        except InventoryTransfer.DoesNotExist:
            return Response(
                {'error': 'Transfer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            InventoryTransferService.approve_transfer(transfer, request.user)
            
            return Response({
                'message': 'Transfer approved',
                'transfer_id': str(transfer.id),
                'status': transfer.status
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsStewardOrAdmin],
            url_path='transfers/(?P<transfer_id>[^/.]+)/complete')
    def complete_transfer(self, request, transfer_id=None):
        """Complete an in-transit transfer (stewards at destination hub)."""
        from .transfer_service import InventoryTransferService
        from .models import InventoryTransfer
        
        try:
            transfer = InventoryTransfer.objects.get(pk=transfer_id)
        except InventoryTransfer.DoesNotExist:
            return Response(
                {'error': 'Transfer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notes = request.data.get('notes', '')
        
        try:
            destination_item = InventoryTransferService.complete_transfer(
                transfer, request.user, notes
            )
            
            return Response({
                'message': 'Transfer completed',
                'transfer_id': str(transfer.id),
                'destination_item_id': str(destination_item.id),
                'status': transfer.status
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsStewardOrAdmin],
            url_path='transfers/(?P<transfer_id>[^/.]+)/cancel')
    def cancel_transfer(self, request, transfer_id=None):
        """Cancel a pending or in-transit transfer."""
        from .transfer_service import InventoryTransferService
        from .models import InventoryTransfer
        
        try:
            transfer = InventoryTransfer.objects.get(pk=transfer_id)
        except InventoryTransfer.DoesNotExist:
            return Response(
                {'error': 'Transfer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reason = request.data.get('reason', 'No reason provided')
        
        try:
            InventoryTransferService.cancel_transfer(transfer, request.user, reason)
            
            return Response({
                'message': 'Transfer cancelled',
                'transfer_id': str(transfer.id),
                'status': transfer.status
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )