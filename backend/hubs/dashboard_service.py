"""
Hub dashboard service for stewards.
Provides comprehensive hub management data and analytics.
"""
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta


class HubDashboardService:
    """Service for generating hub dashboard data for stewards."""
    
    @staticmethod
    def get_dashboard_data(hub, time_range_days=30):
        """
        Get comprehensive dashboard data for a hub.
        
        Args:
            hub: Hub instance
            time_range_days: Number of days for analytics (default 30)
        
        Returns:
            dict with dashboard sections
        """
        from reservations.models import Reservation
        from inventory.models import InventoryItem
        from community.models import Feedback
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        now = timezone.now()
        date_threshold = now - timedelta(days=time_range_days)
        today = now.date()
        
        # Active reservations
        active_reservations = Reservation.objects.filter(
            hub=hub,
            status__in=['confirmed', 'picked_up']
        ).select_related('user', 'item').order_by('pickup_date')
        
        # Upcoming pickups (next 7 days)
        upcoming_pickups = Reservation.objects.filter(
            hub=hub,
            status='confirmed',
            pickup_date__gte=today,
            pickup_date__lte=today + timedelta(days=7)
        ).select_related('user', 'item').order_by('pickup_date')
        
        # Overdue items
        overdue_items = Reservation.objects.filter(
            hub=hub,
            status='picked_up',
            expected_return_date__lt=today
        ).select_related('user', 'item').order_by('expected_return_date')
        
        # Extension requests
        extension_requests = Reservation.objects.filter(
            hub=hub,
            extension_requested=True,
            extension_approved=False,
            status='picked_up'
        ).select_related('user', 'item').order_by('-updated_at')
        
        # Inventory summary
        inventory_stats = {
            'total_items': InventoryItem.objects.filter(hub=hub).count(),
            'active_items': InventoryItem.objects.filter(hub=hub, status='active').count(),
            'total_quantity': InventoryItem.objects.filter(hub=hub).aggregate(
                total=Sum('quantity_total')
            )['total'] or 0,
            'available_quantity': InventoryItem.objects.filter(hub=hub).aggregate(
                available=Sum('quantity_available')
            )['available'] or 0,
            'flagged_items': InventoryItem.objects.filter(hub=hub, is_flagged=True).count(),
            'damaged_items': InventoryItem.objects.filter(hub=hub, status='damaged').count(),
        }
        
        inventory_stats['utilization_rate'] = (
            ((inventory_stats['total_quantity'] - inventory_stats['available_quantity']) / 
             inventory_stats['total_quantity'] * 100)
            if inventory_stats['total_quantity'] > 0 else 0
        )
        
        # Reservation stats (time range)
        reservation_stats = {
            'total_reservations': Reservation.objects.filter(
                hub=hub,
                created_at__gte=date_threshold
            ).count(),
            'completed_reservations': Reservation.objects.filter(
                hub=hub,
                status='returned',
                actual_return_date__gte=date_threshold.date()
            ).count(),
            'cancelled_reservations': Reservation.objects.filter(
                hub=hub,
                status='cancelled',
                updated_at__gte=date_threshold
            ).count(),
            'active_count': active_reservations.count(),
            'overdue_count': overdue_items.count(),
        }
        
        # Calculate average return time
        completed_with_dates = Reservation.objects.filter(
            hub=hub,
            status='returned',
            actual_return_date__gte=date_threshold.date(),
            pickup_date__isnull=False,
            actual_return_date__isnull=False
        )
        
        if completed_with_dates.exists():
            avg_days = sum([
                (r.actual_return_date - r.pickup_date).days 
                for r in completed_with_dates
            ]) / completed_with_dates.count()
            reservation_stats['avg_borrow_duration_days'] = round(avg_days, 1)
        else:
            reservation_stats['avg_borrow_duration_days'] = 0
        
        # User activity stats
        user_stats = {
            'active_borrowers': Reservation.objects.filter(
                hub=hub,
                status__in=['confirmed', 'picked_up'],
            ).values('user').distinct().count(),
            'new_users': User.objects.filter(
                assigned_hub=hub,
                created_at__gte=date_threshold
            ).count(),
            'restricted_users': User.objects.filter(
                assigned_hub=hub,
                borrowing_restricted_until__gt=now
            ).count(),
        }
        
        # Feedback and incidents
        feedback_stats = {
            'pending_incidents': Feedback.objects.filter(
                item__hub=hub,
                type='incident',
                status='pending'
            ).count(),
            'positive_feedback': Feedback.objects.filter(
                item__hub=hub,
                type='positive',
                created_at__gte=date_threshold
            ).count(),
            'average_rating': Feedback.objects.filter(
                item__hub=hub,
                rating__isnull=False,
                created_at__gte=date_threshold
            ).aggregate(avg=Avg('rating'))['avg'] or 0,
        }
        
        # Most borrowed categories
        popular_categories = InventoryItem.objects.filter(
            hub=hub,
            reservations__created_at__gte=date_threshold
        ).values('category').annotate(
            reservation_count=Count('reservations')
        ).order_by('-reservation_count')[:5]
        
        # Most borrowed items
        popular_items = InventoryItem.objects.filter(
            hub=hub,
            reservations__created_at__gte=date_threshold
        ).annotate(
            reservation_count=Count('reservations')
        ).order_by('-reservation_count')[:10]
        
        return {
            'hub_info': {
                'id': str(hub.id),
                'name': hub.name,
                'address': hub.address,
            },
            'overview': {
                'active_reservations': reservation_stats['active_count'],
                'upcoming_pickups': upcoming_pickups.count(),
                'overdue_items': reservation_stats['overdue_count'],
                'pending_incidents': feedback_stats['pending_incidents'],
                'extension_requests': extension_requests.count(),
            },
            'active_reservations': HubDashboardService._serialize_reservations(active_reservations),
            'upcoming_pickups': HubDashboardService._serialize_reservations(upcoming_pickups),
            'overdue_items': HubDashboardService._serialize_reservations(overdue_items),
            'extension_requests': HubDashboardService._serialize_reservations(extension_requests),
            'inventory_stats': inventory_stats,
            'reservation_stats': reservation_stats,
            'user_stats': user_stats,
            'feedback_stats': feedback_stats,
            'popular_categories': list(popular_categories),
            'popular_items': [
                {
                    'id': str(item.id),
                    'name': item.name,
                    'category': item.category,
                    'reservation_count': item.reservation_count
                }
                for item in popular_items
            ],
            'time_range_days': time_range_days,
            'generated_at': now.isoformat(),
        }
    
    @staticmethod
    def _serialize_reservations(reservations):
        """Helper to serialize reservation querysets."""
        return [
            {
                'id': str(r.id),
                'user': {
                    'id': str(r.user.id),
                    'name': r.user.get_full_name(),
                    'email': r.user.email,
                },
                'item': {
                    'id': str(r.item.id),
                    'name': r.item.name,
                    'category': r.item.category,
                },
                'status': r.status,
                'pickup_date': r.pickup_date.isoformat() if r.pickup_date else None,
                'expected_return_date': r.expected_return_date.isoformat() if r.expected_return_date else None,
                'actual_return_date': r.actual_return_date.isoformat() if r.actual_return_date else None,
                'extension_requested': r.extension_requested,
                'extension_approved': r.extension_approved,
                'days_overdue': (timezone.now().date() - r.expected_return_date).days 
                    if r.status == 'picked_up' and r.expected_return_date < timezone.now().date() 
                    else 0,
            }
            for r in reservations
        ]
    
    @staticmethod
    def get_quick_stats(hub):
        """Get quick overview stats for hub (lightweight)."""
        from reservations.models import Reservation
        from inventory.models import InventoryItem
        from community.models import Feedback
        
        today = timezone.now().date()
        
        return {
            'active_reservations': Reservation.objects.filter(
                hub=hub,
                status__in=['confirmed', 'picked_up']
            ).count(),
            'overdue_items': Reservation.objects.filter(
                hub=hub,
                status='picked_up',
                expected_return_date__lt=today
            ).count(),
            'pending_incidents': Feedback.objects.filter(
                item__hub=hub,
                type='incident',
                status='pending'
            ).count(),
            'flagged_items': InventoryItem.objects.filter(
                hub=hub,
                is_flagged=True
            ).count(),
            'available_items': InventoryItem.objects.filter(
                hub=hub,
                status='active',
                quantity_available__gt=0
            ).count(),
        }
