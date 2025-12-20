"""
Partner API Views
Provides endpoints for partner account management, analytics, and sponsored content
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Partner
from .serializers import (
    PartnerSerializer,
    PartnerListSerializer,
    PartnerAnalyticsSerializer
)
from users.permissions import IsAdminOrReadOnly


class PartnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for partner account management
    - List: All authenticated users (for browsing partner resources)
    - Create/Update/Delete: Admin only
    - Retrieve: Authenticated users
    """
    queryset = Partner.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['organization_name', 'contact_email']
    ordering_fields = ['organization_name', 'subscription_tier', 'subscription_end', 'created_at']
    ordering = ['organization_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PartnerListSerializer
        return PartnerSerializer
    
    def get_permissions(self):
        """
        - List/Retrieve: Authenticated users
        - Create/Update/Delete: Admin only
        """
        if self.action in ['list', 'retrieve', 'active_partners', 'sponsored_categories']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by subscription tier
        tier_filter = self.request.query_params.get('tier')
        if tier_filter:
            queryset = queryset.filter(subscription_tier=tier_filter)
        
        # Active partners only
        if self.request.query_params.get('active_only') == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='active',
                subscription_start__lte=today,
                subscription_end__gte=today
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create partner with automatic status calculation"""
        partner = serializer.save()
        
        # Check and update subscription status immediately
        self._update_subscription_status(partner)
        
        return partner
    
    def perform_update(self, serializer):
        """Update partner and refresh subscription status"""
        partner = serializer.save()
        
        # Check and update subscription status
        self._update_subscription_status(partner)
        
        return partner
    
    def _update_subscription_status(self, partner):
        """Update partner subscription status based on dates"""
        today = timezone.now().date()
        
        if partner.subscription_end < today:
            partner.status = 'expired'
            # Clear sponsored categories when expired
            partner.sponsored_categories = []
            partner.save(update_fields=['status', 'sponsored_categories'])
        elif partner.subscription_start <= today <= partner.subscription_end:
            if partner.status != 'suspended':  # Don't override manual suspension
                partner.status = 'active'
                partner.save(update_fields=['status'])
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_partners(self, request):
        """
        Get list of currently active partners.
        Useful for displaying partner resources to users.
        """
        today = timezone.now().date()
        active = self.queryset.filter(
            status='active',
            subscription_start__lte=today,
            subscription_end__gte=today
        )
        
        serializer = PartnerListSerializer(active, many=True)
        return Response({
            'count': active.count(),
            'partners': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def sponsored_categories(self, request):
        """
        Get all currently sponsored categories across all active partners.
        Returns unique category list with partner details.
        """
        today = timezone.now().date()
        active_partners = self.queryset.filter(
            status='active',
            subscription_start__lte=today,
            subscription_end__gte=today
        )
        
        # Collect sponsored categories with partner info
        sponsored = []
        for partner in active_partners:
            if partner.sponsored_categories:
                for category in partner.sponsored_categories:
                    sponsored.append({
                        'category': category,
                        'partner_id': str(partner.id),
                        'partner_name': partner.organization_name,
                        'tier': partner.subscription_tier
                    })
        
        return Response({
            'count': len(sponsored),
            'sponsored_categories': sponsored
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def renew(self, request, pk=None):
        """
        Renew partner subscription.
        Requires admin permissions.
        Expects 'duration_days' in request data (default: 365).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can renew subscriptions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partner = self.get_object()
        duration_days = int(request.data.get('duration_days', 365))
        
        # Calculate new subscription end date
        today = timezone.now().date()
        start_date = max(partner.subscription_end, today)  # Start from current end or today
        new_end = start_date + timedelta(days=duration_days)
        
        partner.subscription_end = new_end
        partner.status = 'active'
        partner.save(update_fields=['subscription_end', 'status'])
        
        serializer = self.get_serializer(partner)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def suspend(self, request, pk=None):
        """
        Suspend partner subscription.
        Requires admin permissions.
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can suspend subscriptions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partner = self.get_object()
        partner.status = 'suspended'
        partner.save(update_fields=['status'])
        
        serializer = self.get_serializer(partner)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        """
        Activate suspended partner subscription.
        Requires admin permissions.
        Checks that subscription dates are still valid.
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can activate subscriptions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partner = self.get_object()
        today = timezone.now().date()
        
        # Check if subscription dates are valid
        if partner.subscription_end < today:
            return Response(
                {'error': 'Cannot activate expired subscription. Please renew first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        partner.status = 'active'
        partner.save(update_fields=['status'])
        
        serializer = self.get_serializer(partner)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request, pk=None):
        """
        Get privacy-safe analytics for a partner.
        Premium and Enterprise tiers only.
        """
        partner = self.get_object()
        
        # Check tier access
        if partner.subscription_tier not in ['premium', 'enterprise']:
            return Response(
                {'error': 'Analytics only available for Premium and Enterprise tiers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check partner is active
        today = timezone.now().date()
        if partner.status != 'active' or partner.subscription_end < today:
            return Response(
                {'error': 'Analytics only available for active subscriptions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate analytics data
        analytics_data = self._generate_partner_analytics(partner)
        
        serializer = PartnerAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    def _generate_partner_analytics(self, partner):
        """
        Generate privacy-safe analytics for partner.
        Aggregates data without exposing individual user information.
        """
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Get demand data for sponsored categories
        if not partner.sponsored_categories:
            return self._empty_analytics(partner)
        
        # Aggregate category demand (privacy-safe)
        category_demand = {}
        for category in partner.sponsored_categories:
            # Count items in category
            item_count = InventoryItem.objects.filter(
                category=category,
                is_active=True
            ).count()
            
            # Count reservations for category (last 30 days)
            reservation_count = Reservation.objects.filter(
                item__category=category,
                created_at__gte=thirty_days_ago
            ).count()
            
            category_demand[category] = {
                'item_count': item_count,
                'reservation_count': reservation_count
            }
        
        # Calculate aggregated metrics
        total_demand = sum(d['reservation_count'] for d in category_demand.values())
        avg_demand = total_demand / len(category_demand) if category_demand else 0
        
        # Get unique hub count (privacy-safe aggregation)
        unique_hubs = InventoryItem.objects.filter(
            category__in=partner.sponsored_categories,
            is_active=True
        ).values('hub').distinct().count()
        
        # Top performing categories
        top_categories = sorted(
            category_demand.items(),
            key=lambda x: x[1]['reservation_count'],
            reverse=True
        )[:5]
        
        return {
            'partner_id': partner.id,
            'organization_name': partner.organization_name,
            'subscription_tier': partner.subscription_tier,
            'total_category_demand': total_demand,
            'sponsored_category_views': total_demand,  # Simplified
            'top_categories': [
                {'category': cat, **data} for cat, data in top_categories
            ],
            'weekly_trend': {},  # Placeholder for time-series data
            'monthly_trend': {},  # Placeholder for time-series data
            'unique_hub_count': unique_hubs,
            'avg_category_demand': avg_demand,
            'data_period_start': thirty_days_ago,
            'data_period_end': today,
            'last_updated': timezone.now()
        }
    
    def _empty_analytics(self, partner):
        """Return empty analytics structure"""
        today = timezone.now().date()
        return {
            'partner_id': partner.id,
            'organization_name': partner.organization_name,
            'subscription_tier': partner.subscription_tier,
            'total_category_demand': 0,
            'sponsored_category_views': 0,
            'top_categories': [],
            'weekly_trend': {},
            'monthly_trend': {},
            'unique_hub_count': 0,
            'avg_category_demand': 0.0,
            'data_period_start': today - timedelta(days=30),
            'data_period_end': today,
            'last_updated': timezone.now()
        }
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def expiring_soon(self, request):
        """
        Get partners with subscriptions expiring in the next 30 days.
        Admin only - for renewal reminders.
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can view expiring subscriptions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        thirty_days_from_now = today + timedelta(days=30)
        
        expiring = self.queryset.filter(
            status='active',
            subscription_end__gte=today,
            subscription_end__lte=thirty_days_from_now
        ).order_by('subscription_end')
        
        serializer = PartnerListSerializer(expiring, many=True)
        return Response({
            'count': expiring.count(),
            'expiring_partners': serializer.data
        })

