from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.http import HttpResponse
from .models import Hub, Event, Announcement
from .serializers import HubSerializer, HubListSerializer, EventSerializer, AnnouncementSerializer
from users.permissions import IsStewardOrAdmin, IsAdminUser
from .admin_dashboard_service import PlatformAdminService


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
    
    @action(detail=True, methods=['get'], permission_classes=[IsStewardOrAdmin])
    def dashboard(self, request, pk=None):
        """
        Get comprehensive hub dashboard for stewards.
        Includes active reservations, upcoming pickups, overdue items, and analytics.
        """
        from .dashboard_service import HubDashboardService
        
        hub = self.get_object()
        
        # Check if user is steward at this hub or admin
        if request.user.role != 'admin' and not hub.stewards.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not authorized to view this hub dashboard'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get time range from query params (default 30 days)
        time_range = int(request.query_params.get('days', 30))
        
        dashboard_data = HubDashboardService.get_dashboard_data(hub, time_range_days=time_range)
        
        return Response(dashboard_data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsStewardOrAdmin])
    def quick_stats(self, request, pk=None):
        """
        Get quick overview stats for hub (lightweight endpoint).
        For quick checks without full dashboard data.
        """
        from .dashboard_service import HubDashboardService
        
        hub = self.get_object()
        
        # Check permissions
        if request.user.role != 'admin' and not hub.stewards.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not authorized to view this hub stats'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = HubDashboardService.get_quick_stats(hub)
        
        return Response(stats)


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


class PlatformAdminViewSet(viewsets.ViewSet):
    """ViewSet for platform administrator dashboard and analytics."""
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('days', int, description='Time range in days (default: 30)'),
        ]
    )
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Get comprehensive platform-wide metrics.
        Accessible only to platform administrators.
        """
        days = int(request.query_params.get('days', 30))
        metrics = PlatformAdminService.get_platform_metrics(time_range_days=days)
        
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def hub_comparison(self, request):
        """
        Compare performance metrics across all hubs.
        Shows ranking and key statistics for each hub.
        """
        comparison = PlatformAdminService.get_hub_performance_comparison()
        
        return Response({
            'total_hubs': len(comparison),
            'hubs': comparison
        })
    
    @extend_schema(
        parameters=[
            OpenApiParameter('type', str, description='Data type to export (users/items/reservations/all)'),
            OpenApiParameter('format', str, description='Export format (csv/json)'),
        ]
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export platform data in CSV or JSON format.
        Provides comprehensive data dumps for external analysis.
        """
        data_type = request.query_params.get('type', 'all')
        export_format = request.query_params.get('format', 'csv')
        
        if data_type not in ['users', 'items', 'reservations', 'all']:
            return Response(
                {'error': 'Invalid data type. Choose: users, items, reservations, or all'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if export_format not in ['csv', 'json']:
            return Response(
                {'error': 'Invalid format. Choose: csv or json'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exported_data = PlatformAdminService.export_data(data_type, export_format)
        
        # Set appropriate content type and filename
        if export_format == 'csv':
            response = HttpResponse(exported_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="flokr_export_{data_type}.csv"'
        else:
            response = HttpResponse(exported_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="flokr_export_{data_type}.json"'
        
        return response

