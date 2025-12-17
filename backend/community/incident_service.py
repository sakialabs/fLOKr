"""
Incident reporting and feedback service.
Handles multi-report flagging, steward notifications, and resolution tracking.
"""
from django.utils import timezone
from django.db.models import Count, Avg
from django.db import models
from users.notifications import send_notification


class IncidentService:
    """Service for handling incident reports and feedback."""
    
    # Thresholds
    INCIDENT_FLAG_THRESHOLD = 3  # Flag item after 3 incident reports
    
    @staticmethod
    def process_incident_report(feedback):
        """
        Process an incident report.
        - Notify stewards
        - Check if item should be flagged
        - Update item incident count
        """
        if feedback.type != 'incident':
            return
        
        # Notify stewards at the hub
        if feedback.item and feedback.item.hub:
            IncidentService._notify_stewards(feedback)
        
        # Update item incident count and check flagging
        if feedback.item:
            IncidentService._update_item_incident_count(feedback.item)
    
    @staticmethod
    def _notify_stewards(feedback):
        """Send notification to all stewards at the item's hub."""
        hub = feedback.item.hub
        stewards = hub.stewards.all()
        
        for steward in stewards:
            send_notification(
                user=steward,
                notification_type='incident_report',
                title=f"Incident Report: {feedback.item.name}",
                message=f"User {feedback.user.get_full_name()} reported an incident with {feedback.item.name}. Please review.",
                data={
                    'feedback_id': str(feedback.id),
                    'item_id': str(feedback.item.id),
                    'hub_id': str(hub.id),
                    'urgency': 'high' if feedback.item.incident_report_count >= 2 else 'medium'
                }
            )
    
    @staticmethod
    def _update_item_incident_count(item):
        """Update item's incident report count and flag if threshold reached."""
        from community.models import Feedback
        
        # Count incident reports for this item
        incident_count = Feedback.objects.filter(
            item=item,
            type='incident'
        ).count()
        
        item.incident_report_count = incident_count
        
        # Flag item if threshold reached
        if incident_count >= IncidentService.INCIDENT_FLAG_THRESHOLD and not item.is_flagged:
            item.is_flagged = True
            item.flagged_at = timezone.now()
            item.status = 'damaged'  # Auto-mark as damaged
            
            # Notify stewards about flagging
            IncidentService._notify_stewards_about_flagging(item)
        
        item.save()
    
    @staticmethod
    def _notify_stewards_about_flagging(item):
        """Notify stewards when an item gets flagged."""
        stewards = item.hub.stewards.all()
        
        for steward in stewards:
            send_notification(
                user=steward,
                notification_type='item_flagged',
                title=f"Item Flagged: {item.name}",
                message=f"{item.name} has been automatically flagged after {item.incident_report_count} incident reports. Please inspect and resolve.",
                data={
                    'item_id': str(item.id),
                    'hub_id': str(item.hub.id),
                    'incident_count': item.incident_report_count,
                    'urgency': 'urgent'
                }
            )
    
    @staticmethod
    def resolve_feedback(feedback, resolved_by, resolution_notes):
        """
        Mark feedback as resolved.
        
        Args:
            feedback: Feedback instance
            resolved_by: User who resolved it (steward/admin)
            resolution_notes: Notes about how it was resolved
        """
        feedback.status = 'resolved'
        feedback.reviewed_by = resolved_by
        feedback.resolution_notes = resolution_notes
        feedback.resolved_at = timezone.now()
        feedback.save()
        
        # Notify the feedback submitter
        send_notification(
            user=feedback.user,
            notification_type='feedback_resolved',
            title="Your feedback has been addressed",
            message=f"Thank you for your feedback. A steward has reviewed and resolved your concern about {feedback.item.name if feedback.item else 'your issue'}.",
            data={
                'feedback_id': str(feedback.id),
                'resolution_notes': resolution_notes
            }
        )
    
    @staticmethod
    def unflag_item(item, resolved_by, notes):
        """
        Unflag an item after resolution.
        
        Args:
            item: InventoryItem instance
            resolved_by: User who resolved it
            notes: Resolution notes
        """
        item.is_flagged = False
        item.flagged_at = None
        
        # Optionally reset incident count if item is fixed
        # item.incident_report_count = 0
        
        # Re-activate item if it was damaged
        if item.status == 'damaged':
            item.status = 'active'
        
        item.save()
        
        # Log resolution (we can add this to Feedback as a resolution record)
        from community.models import Feedback
        Feedback.objects.create(
            user=resolved_by,
            item=item,
            type='positive',
            comment=f"Item issue resolved: {notes}",
            status='resolved',
            reviewed_by=resolved_by,
            resolution_notes=notes,
            resolved_at=timezone.now()
        )
    
    @staticmethod
    def get_pending_incidents(hub=None):
        """
        Get pending incident reports, optionally filtered by hub.
        
        Returns incidents ordered by priority (flagged items first, then by report count).
        """
        from community.models import Feedback
        from django.db.models import Q
        
        queryset = Feedback.objects.filter(
            type='incident',
            status='pending'
        ).select_related('user', 'item', 'item__hub')
        
        if hub:
            queryset = queryset.filter(item__hub=hub)
        
        # Order by flagged items first, then by incident count
        queryset = queryset.order_by(
            '-item__is_flagged',
            '-item__incident_report_count',
            '-created_at'
        )
        
        return queryset
    
    @staticmethod
    def get_feedback_stats(hub=None):
        """Get feedback statistics for dashboard."""
        from community.models import Feedback
        
        base_query = Feedback.objects.all()
        if hub:
            base_query = base_query.filter(item__hub=hub)
        
        stats = {
            'pending_incidents': base_query.filter(type='incident', status='pending').count(),
            'flagged_items': base_query.filter(item__is_flagged=True).values('item').distinct().count(),
            'positive_feedback_count': base_query.filter(type='positive').count(),
            'average_rating': base_query.filter(rating__isnull=False).aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating'] or 0,
            'recent_resolutions': base_query.filter(
                status='resolved',
                resolved_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        return stats
