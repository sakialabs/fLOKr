from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Hub, Event, Announcement
from .serializers import HubSerializer, HubListSerializer, EventSerializer, AnnouncementSerializer
from users.permissions import IsStewardOrAdmin, IsAdminUser


class HubViewSet(viewsets.ModelViewSet):
    """ViewSet for Hub management."""
    queryset = Hub.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HubListSerializer
        return HubSerializer
    
    def get_permissions(self):
        """Admin-only for create, update, delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('lat', float, description='Latitude'),
            OpenApiParameter('lng', float, description='Longitude'),
        ]
    )
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get hubs near user location, sorted by distance."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response(
                {'error': 'lat and lng parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_location = Point(float(lng), float(lat), srid=4326)
            hubs = Hub.objects.filter(status='active').annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')
            
            serializer = self.get_serializer(hubs, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get hub analytics (stewards and admins only)."""
        hub = self.get_object()
        
        # Check if user is steward of this hub or admin
        if not (request.user.role in ['admin', 'steward'] or 
                request.user in hub.stewards.all()):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analytics = {
            'total_items': hub.current_inventory_count,
            'capacity': hub.capacity,
            'utilization': (hub.current_inventory_count / hub.capacity * 100) if hub.capacity > 0 else 0,
            'active_reservations': hub.reservations.filter(status__in=['pending', 'confirmed', 'picked_up']).count(),
            'steward_count': hub.stewards.count(),
        }
        
        return Response(analytics)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for hub events."""
    queryset = Event.objects.select_related('hub', 'organizer').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['event_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by hub
        hub_id = self.request.query_params.get('hub')
        if hub_id:
            queryset = queryset.filter(hub_id=hub_id)
        
        # Filter upcoming events only
        if self.request.query_params.get('upcoming') == 'true':
            queryset = queryset.filter(event_date__gte=timezone.now())
        
        # Filter past events
        if self.request.query_params.get('past') == 'true':
            queryset = queryset.filter(event_date__lt=timezone.now())
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """ViewSet for hub announcements."""
    queryset = Announcement.objects.select_related('hub', 'author').all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by hub
        hub_id = self.request.query_params.get('hub')
        if hub_id:
            queryset = queryset.filter(hub_id=hub_id)
        
        # Filter active announcements only
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(
                active_until__isnull=True
            ) | queryset.filter(active_until__gte=timezone.now().date())
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
