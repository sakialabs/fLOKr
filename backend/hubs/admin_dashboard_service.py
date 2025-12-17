"""
Platform administrator dashboard service.
Provides platform-wide metrics, analytics, and hub comparisons.
"""
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import csv
from io import StringIO


class PlatformAdminService:
    """Service for platform-wide administrative analytics."""
    
    @staticmethod
    def get_platform_metrics(time_range_days=30):
        """
        Get comprehensive platform-wide metrics.
        
        Args:
            time_range_days: Number of days for time-based metrics
        
        Returns:
            dict with platform metrics
        """
        from django.contrib.auth import get_user_model
        from inventory.models import InventoryItem, InventoryTransfer
        from reservations.models import Reservation
        from hubs.models import Hub
        from community.models import Feedback, Badge, UserBadge
        
        User = get_user_model()
        now = timezone.now()
        date_threshold = now - timedelta(days=time_range_days)
        
        # User metrics
        user_metrics = {
            'total_users': User.objects.count(),
            'newcomers': User.objects.filter(role='newcomer').count(),
            'community_members': User.objects.filter(role='community_member').count(),
            'stewards': User.objects.filter(role='steward').count(),
            'partners': User.objects.filter(role='partner').count(),
            'new_registrations': User.objects.filter(created_at__gte=date_threshold).count(),
            'active_borrowers': Reservation.objects.filter(
                created_at__gte=date_threshold
            ).values('user').distinct().count(),
            'mentors': User.objects.filter(is_mentor=True).count(),
            'restricted_users': User.objects.filter(
                borrowing_restricted_until__gt=now
            ).count(),
        }
        
        # Hub metrics
        hub_metrics = {
            'total_hubs': Hub.objects.count(),
            'active_hubs': Hub.objects.filter(status='active').count(),
            'total_stewards': User.objects.filter(role='steward').count(),
        }
        
        # Inventory metrics
        inventory_metrics = {
            'total_items': InventoryItem.objects.count(),
            'active_items': InventoryItem.objects.filter(status='active').count(),
            'total_quantity': InventoryItem.objects.aggregate(
                total=Sum('quantity_total')
            )['total'] or 0,
            'available_quantity': InventoryItem.objects.aggregate(
                available=Sum('quantity_available')
            )['available'] or 0,
            'flagged_items': InventoryItem.objects.filter(is_flagged=True).count(),
            'new_items': InventoryItem.objects.filter(created_at__gte=date_threshold).count(),
        }
        
        inventory_metrics['utilization_rate'] = (
            ((inventory_metrics['total_quantity'] - inventory_metrics['available_quantity']) / 
             inventory_metrics['total_quantity'] * 100)
            if inventory_metrics['total_quantity'] > 0 else 0
        )
        
        # Reservation metrics
        reservation_metrics = {
            'total_reservations': Reservation.objects.count(),
            'active_reservations': Reservation.objects.filter(
                status__in=['confirmed', 'picked_up']
            ).count(),
            'completed_reservations': Reservation.objects.filter(
                status='returned',
                actual_return_date__gte=date_threshold.date()
            ).count(),
            'overdue_reservations': Reservation.objects.filter(
                status='picked_up',
                expected_return_date__lt=now.date()
            ).count(),
            'new_reservations': Reservation.objects.filter(
                created_at__gte=date_threshold
            ).count(),
        }
        
        # Calculate completion rate
        completed = Reservation.objects.filter(status='returned').count()
        total_non_pending = Reservation.objects.exclude(status='pending').count()
        reservation_metrics['completion_rate'] = (
            (completed / total_non_pending * 100) if total_non_pending > 0 else 0
        )
        
        # Transfer metrics
        transfer_metrics = {
            'total_transfers': InventoryTransfer.objects.count(),
            'pending_transfers': InventoryTransfer.objects.filter(status='pending').count(),
            'in_transit_transfers': InventoryTransfer.objects.filter(status='in_transit').count(),
            'completed_transfers': InventoryTransfer.objects.filter(
                status='completed',
                completed_at__gte=date_threshold
            ).count(),
        }
        
        # Feedback metrics
        feedback_metrics = {
            'total_feedback': Feedback.objects.count(),
            'positive_feedback': Feedback.objects.filter(type='positive').count(),
            'incidents': Feedback.objects.filter(type='incident').count(),
            'pending_incidents': Feedback.objects.filter(
                type='incident',
                status='pending'
            ).count(),
            'average_rating': Feedback.objects.filter(
                rating__isnull=False
            ).aggregate(avg=Avg('rating'))['avg'] or 0,
        }
        
        # Gamification metrics
        gamification_metrics = {
            'total_badges': Badge.objects.count(),
            'badges_awarded': UserBadge.objects.count(),
            'average_reputation': User.objects.aggregate(
                avg=Avg('reputation_score')
            )['avg'] or 0,
        }
        
        # Top categories
        top_categories = InventoryItem.objects.values('category').annotate(
            item_count=Count('id'),
            reservation_count=Count('reservations')
        ).order_by('-reservation_count')[:10]
        
        return {
            'platform_overview': {
                'generated_at': now.isoformat(),
                'time_range_days': time_range_days,
            },
            'users': user_metrics,
            'hubs': hub_metrics,
            'inventory': inventory_metrics,
            'reservations': reservation_metrics,
            'transfers': transfer_metrics,
            'feedback': feedback_metrics,
            'gamification': gamification_metrics,
            'top_categories': list(top_categories),
        }
    
    @staticmethod
    def get_hub_performance_comparison():
        """
        Compare performance metrics across all hubs.
        
        Returns:
            list of hub performance data
        """
        from hubs.models import Hub
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        from community.models import Feedback
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        hubs = Hub.objects.all()
        
        comparison_data = []
        
        for hub in hubs:
            # Item stats
            total_items = InventoryItem.objects.filter(hub=hub).count()
            active_items = InventoryItem.objects.filter(hub=hub, status='active').count()
            total_quantity = InventoryItem.objects.filter(hub=hub).aggregate(
                total=Sum('quantity_total')
            )['total'] or 0
            available_quantity = InventoryItem.objects.filter(hub=hub).aggregate(
                available=Sum('quantity_available')
            )['available'] or 0
            
            # Reservation stats
            total_reservations = Reservation.objects.filter(hub=hub).count()
            active_reservations = Reservation.objects.filter(
                hub=hub,
                status__in=['confirmed', 'picked_up']
            ).count()
            completed_reservations = Reservation.objects.filter(
                hub=hub,
                status='returned'
            ).count()
            
            # User stats
            assigned_users = User.objects.filter(assigned_hub=hub).count()
            stewards = hub.stewards.count()
            
            # Feedback stats
            avg_rating = Feedback.objects.filter(
                item__hub=hub,
                rating__isnull=False
            ).aggregate(avg=Avg('rating'))['avg'] or 0
            
            pending_incidents = Feedback.objects.filter(
                item__hub=hub,
                type='incident',
                status='pending'
            ).count()
            
            # Calculate utilization
            utilization_rate = (
                ((total_quantity - available_quantity) / total_quantity * 100)
                if total_quantity > 0 else 0
            )
            
            # Calculate completion rate
            completion_rate = (
                (completed_reservations / total_reservations * 100)
                if total_reservations > 0 else 0
            )
            
            comparison_data.append({
                'hub_id': str(hub.id),
                'hub_name': hub.name,
                'hub_status': hub.status,
                'total_items': total_items,
                'active_items': active_items,
                'total_quantity': total_quantity,
                'utilization_rate': round(utilization_rate, 2),
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'completion_rate': round(completion_rate, 2),
                'assigned_users': assigned_users,
                'stewards': stewards,
                'average_rating': round(avg_rating, 2),
                'pending_incidents': pending_incidents,
            })
        
        # Sort by total reservations (most active first)
        comparison_data.sort(key=lambda x: x['total_reservations'], reverse=True)
        
        return comparison_data
    
    @staticmethod
    def export_data(data_type='all', format='csv'):
        """
        Export platform data to CSV or JSON.
        
        Args:
            data_type: Type of data to export ('users', 'items', 'reservations', 'all')
            format: Export format ('csv' or 'json')
        
        Returns:
            Exported data as string
        """
        from django.contrib.auth import get_user_model
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        
        User = get_user_model()
        
        if format == 'csv':
            output = StringIO()
            
            if data_type in ['users', 'all']:
                writer = csv.writer(output)
                writer.writerow(['ID', 'Email', 'Name', 'Role', 'Hub', 'Reputation', 'Created'])
                
                users = User.objects.select_related('assigned_hub').all()
                for user in users:
                    writer.writerow([
                        str(user.id),
                        user.email,
                        user.get_full_name(),
                        user.role,
                        user.assigned_hub.name if user.assigned_hub else 'N/A',
                        user.reputation_score,
                        user.created_at.isoformat()
                    ])
                
                output.write('\n\n')
            
            if data_type in ['items', 'all']:
                writer = csv.writer(output)
                writer.writerow(['ID', 'Name', 'Hub', 'Category', 'Status', 'Total Qty', 'Available Qty', 'Created'])
                
                items = InventoryItem.objects.select_related('hub').all()
                for item in items:
                    writer.writerow([
                        str(item.id),
                        item.name,
                        item.hub.name,
                        item.category,
                        item.status,
                        item.quantity_total,
                        item.quantity_available,
                        item.created_at.isoformat()
                    ])
                
                output.write('\n\n')
            
            if data_type in ['reservations', 'all']:
                writer = csv.writer(output)
                writer.writerow(['ID', 'User', 'Item', 'Hub', 'Status', 'Pickup Date', 'Return Date', 'Created'])
                
                reservations = Reservation.objects.select_related('user', 'item', 'hub').all()
                for res in reservations:
                    writer.writerow([
                        str(res.id),
                        res.user.get_full_name(),
                        res.item.name,
                        res.hub.name,
                        res.status,
                        res.pickup_date.isoformat() if res.pickup_date else 'N/A',
                        res.expected_return_date.isoformat() if res.expected_return_date else 'N/A',
                        res.created_at.isoformat()
                    ])
            
            return output.getvalue()
        
        else:  # JSON format
            import json
            
            data = {}
            
            if data_type in ['users', 'all']:
                users = User.objects.select_related('assigned_hub').values(
                    'id', 'email', 'first_name', 'last_name', 'role',
                    'assigned_hub__name', 'reputation_score', 'created_at'
                )
                data['users'] = list(users)
            
            if data_type in ['items', 'all']:
                items = InventoryItem.objects.select_related('hub').values(
                    'id', 'name', 'hub__name', 'category', 'status',
                    'quantity_total', 'quantity_available', 'created_at'
                )
                data['items'] = list(items)
            
            if data_type in ['reservations', 'all']:
                reservations = Reservation.objects.select_related('user', 'item', 'hub').values(
                    'id', 'user__first_name', 'user__last_name', 'item__name',
                    'hub__name', 'status', 'pickup_date', 'expected_return_date', 'created_at'
                )
                data['reservations'] = list(reservations)
            
            return json.dumps(data, default=str, indent=2)
