"""
Celery tasks for reservation management.

This module contains background tasks for:
- Automatic reservation expiration
- Overdue item reminders
- Scheduled notification delivery
"""
import logging
from datetime import datetime, timedelta
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from reservations.models import Reservation
from inventory.models import InventoryItem

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='reservations.expire_pending_reservations',
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def expire_pending_reservations(self):
    """
    Expire pending reservations where pickup date has passed.
    
    This task:
    1. Finds all pending reservations with pickup_date in the past
    2. Cancels them and restores inventory availability
    3. Sends notification to users
    
    Runs: Every hour via Celery Beat
    Property: 11 - Automatic reservation expiration
    """
    try:
        today = timezone.now().date()
        
        # Find expired pending reservations
        expired_reservations = Reservation.objects.filter(
            status=Reservation.Status.PENDING,
            pickup_date__lt=today
        ).select_related('user', 'item', 'hub')
        
        expired_count = 0
        failed_count = 0
        
        for reservation in expired_reservations:
            try:
                with transaction.atomic():
                    # Restore inventory (use select_for_update to avoid race conditions)
                    item = InventoryItem.objects.select_for_update().get(id=reservation.item.id)
                    item.quantity_available += reservation.quantity
                    item.save(update_fields=['quantity_available'])
                    
                    # Update reservation status
                    reservation.status = Reservation.Status.CANCELLED
                    reservation.save(update_fields=['status', 'updated_at'])
                    
                    expired_count += 1
                    logger.info(
                        f"Expired reservation {reservation.id} for user {reservation.user.email}"
                    )
                
                # Send notification outside transaction (don't fail if notification fails)
                try:
                    send_expiration_notification.delay(
                        reservation_id=str(reservation.id),
                        user_email=reservation.user.email,
                        item_name=reservation.item.name,
                        pickup_date=reservation.pickup_date.isoformat()
                    )
                except Exception as notif_error:
                    logger.warning(
                        f"Failed to send notification for reservation {reservation.id}: {str(notif_error)}"
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Failed to expire reservation {reservation.id}: {str(e)}",
                    exc_info=True
                )
        
        logger.info(
            f"Reservation expiration complete: {expired_count} expired, {failed_count} failed"
        )
        
        return {
            'expired': expired_count,
            'failed': failed_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in expire_pending_reservations: {str(exc)}", exc_info=True)
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_pickup_reminders',
    max_retries=3,
    default_retry_delay=300,
)
def send_pickup_reminders(self):
    """
    Send reminders for reservations with pickup date tomorrow.
    
    This task:
    1. Finds confirmed reservations with pickup_date = tomorrow
    2. Sends reminder notifications to users
    
    Runs: Daily at 9 AM via Celery Beat
    Property: 36 - Scheduled reminder creation
    """
    try:
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Find reservations with pickup tomorrow
        upcoming_reservations = Reservation.objects.filter(
            status=Reservation.Status.CONFIRMED,
            pickup_date=tomorrow
        ).select_related('user', 'item', 'hub')
        
        reminder_count = 0
        failed_count = 0
        
        for reservation in upcoming_reservations:
            try:
                send_pickup_reminder_notification.delay(
                    reservation_id=str(reservation.id),
                    user_email=reservation.user.email,
                    user_name=reservation.user.get_full_name(),
                    item_name=reservation.item.name,
                    hub_name=reservation.hub.name,
                    hub_address=reservation.hub.address,
                    pickup_date=reservation.pickup_date.isoformat()
                )
                
                reminder_count += 1
                logger.info(
                    f"Sent pickup reminder for reservation {reservation.id}"
                )
                
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Failed to send pickup reminder for reservation {reservation.id}: {str(e)}",
                    exc_info=True
                )
        
        logger.info(
            f"Pickup reminders complete: {reminder_count} sent, {failed_count} failed"
        )
        
        return {
            'reminders_sent': reminder_count,
            'failed': failed_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in send_pickup_reminders: {str(exc)}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_return_reminders',
    max_retries=3,
    default_retry_delay=300,
)
def send_return_reminders(self):
    """
    Send reminders for items due to be returned tomorrow.
    
    This task:
    1. Finds picked-up reservations with expected_return_date = tomorrow
    2. Sends reminder notifications to users
    
    Runs: Daily at 9 AM via Celery Beat
    Property: 36 - Scheduled reminder creation
    """
    try:
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Find reservations with return due tomorrow
        upcoming_returns = Reservation.objects.filter(
            status=Reservation.Status.PICKED_UP,
            expected_return_date=tomorrow
        ).select_related('user', 'item', 'hub')
        
        reminder_count = 0
        failed_count = 0
        
        for reservation in upcoming_returns:
            try:
                send_return_reminder_notification.delay(
                    reservation_id=str(reservation.id),
                    user_email=reservation.user.email,
                    user_name=reservation.user.get_full_name(),
                    item_name=reservation.item.name,
                    hub_name=reservation.hub.name,
                    hub_address=reservation.hub.address,
                    return_date=reservation.expected_return_date.isoformat()
                )
                
                reminder_count += 1
                logger.info(
                    f"Sent return reminder for reservation {reservation.id}"
                )
                
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Failed to send return reminder for reservation {reservation.id}: {str(e)}",
                    exc_info=True
                )
        
        logger.info(
            f"Return reminders complete: {reminder_count} sent, {failed_count} failed"
        )
        
        return {
            'reminders_sent': reminder_count,
            'failed': failed_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in send_return_reminders: {str(exc)}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_overdue_reminders',
    max_retries=3,
    default_retry_delay=300,
)
def send_overdue_reminders(self):
    """
    Send escalating reminders for overdue items.
    
    This task:
    1. Finds picked-up reservations past expected_return_date
    2. Updates status to OVERDUE
    3. Sends escalating reminders (1 day, 3 days, 7 days overdue)
    4. Notifies hub stewards
    
    Runs: Daily at 10 AM via Celery Beat
    Property: 37 - Overdue item reminders
    """
    try:
        today = timezone.now().date()
        
        # Find overdue reservations
        overdue_reservations = Reservation.objects.filter(
            Q(status=Reservation.Status.PICKED_UP) | Q(status=Reservation.Status.OVERDUE),
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).select_related('user', 'item', 'hub')
        
        reminder_count = 0
        status_updated = 0
        failed_count = 0
        
        for reservation in overdue_reservations:
            try:
                days_overdue = (today - reservation.expected_return_date).days
                
                # Update status to OVERDUE if not already
                if reservation.status != Reservation.Status.OVERDUE:
                    with transaction.atomic():
                        reservation.status = Reservation.Status.OVERDUE
                        reservation.save(update_fields=['status', 'updated_at'])
                        status_updated += 1
                
                # Send escalating reminders at specific intervals
                should_send_reminder = (
                    days_overdue == 1 or  # 1 day overdue
                    days_overdue == 3 or  # 3 days overdue
                    days_overdue == 7 or  # 1 week overdue
                    days_overdue % 7 == 0  # Every week after that
                )
                
                if should_send_reminder:
                    # Send to user
                    send_overdue_notification.delay(
                        reservation_id=str(reservation.id),
                        user_email=reservation.user.email,
                        user_name=reservation.user.get_full_name(),
                        item_name=reservation.item.name,
                        hub_name=reservation.hub.name,
                        days_overdue=days_overdue,
                        expected_return_date=reservation.expected_return_date.isoformat()
                    )
                    
                    # Notify stewards for items 3+ days overdue
                    if days_overdue >= 3:
                        notify_stewards_overdue.delay(
                            reservation_id=str(reservation.id),
                            hub_id=str(reservation.hub.id),
                            user_name=reservation.user.get_full_name(),
                            user_email=reservation.user.email,
                            item_name=reservation.item.name,
                            days_overdue=days_overdue
                        )
                    
                    reminder_count += 1
                    logger.info(
                        f"Sent overdue reminder for reservation {reservation.id} "
                        f"({days_overdue} days overdue)"
                    )
                
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Failed to process overdue reservation {reservation.id}: {str(e)}",
                    exc_info=True
                )
        
        logger.info(
            f"Overdue reminders complete: {reminder_count} sent, "
            f"{status_updated} status updated, {failed_count} failed"
        )
        
        return {
            'reminders_sent': reminder_count,
            'status_updated': status_updated,
            'failed': failed_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in send_overdue_reminders: {str(exc)}", exc_info=True)
        raise self.retry(exc=exc)


# ============================================================================
# Notification Tasks
# ============================================================================

@shared_task(
    bind=True,
    name='reservations.send_expiration_notification',
    max_retries=3,
    default_retry_delay=60,
)
def send_expiration_notification(self, reservation_id, user_email, item_name, pickup_date):
    """Send notification when a reservation expires."""
    try:
        from users.notifications import notification_service
        from users.models import User
        
        # Get user
        user = User.objects.get(email=user_email)
        
        # Create push notification
        notification_service.create_notification(
            recipient_id=str(user.id),
            notification_type='reservation',
            title=f"Reservation Expired",
            body=f"Your reservation for '{item_name}' has expired. The pickup date ({pickup_date}) has passed.",
            data={
                'reservation_id': reservation_id,
                'item_name': item_name,
                'action': 'expired'
            },
            send_push=True
        )
        
        logger.info(f"Sent expiration notification for reservation {reservation_id}")
        return {'status': 'sent', 'reservation_id': reservation_id}
        
    except Exception as exc:
        logger.error(
            f"Failed to send expiration notification for {reservation_id}: {str(exc)}",
            exc_info=True
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_pickup_reminder_notification',
    max_retries=3,
    default_retry_delay=60,
)
def send_pickup_reminder_notification(
    self, reservation_id, user_email, user_name, item_name, 
    hub_name, hub_address, pickup_date
):
    """Send pickup reminder notification."""
    try:
        from users.notifications import notification_service
        from users.models import User
        
        # Get user
        user = User.objects.get(email=user_email)
        
        # Create push notification
        notification_service.create_notification(
            recipient_id=str(user.id),
            notification_type='reminder',
            title=f"Pickup Tomorrow",
            body=f"Don't forget to pick up '{item_name}' tomorrow at {hub_name}!",
            data={
                'reservation_id': reservation_id,
                'item_name': item_name,
                'hub_name': hub_name,
                'hub_address': hub_address,
                'pickup_date': pickup_date,
                'action': 'pickup_reminder'
            },
            send_push=True
        )
        
        logger.info(f"Sent pickup reminder for reservation {reservation_id}")
        return {'status': 'sent', 'reservation_id': reservation_id}
        
    except Exception as exc:
        logger.error(
            f"Failed to send pickup reminder for {reservation_id}: {str(exc)}",
            exc_info=True
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_return_reminder_notification',
    max_retries=3,
    default_retry_delay=60,
)
def send_return_reminder_notification(
    self, reservation_id, user_email, user_name, item_name,
    hub_name, hub_address, return_date
):
    """Send return reminder notification."""
    try:
        from users.notifications import notification_service
        from users.models import User
        
        # Get user
        user = User.objects.get(email=user_email)
        
        # Create push notification
        notification_service.create_notification(
            recipient_id=str(user.id),
            notification_type='reminder',
            title=f"Return Due Tomorrow",
            body=f"Please return '{item_name}' to {hub_name} tomorrow. Need more time? Request an extension!",
            data={
                'reservation_id': reservation_id,
                'item_name': item_name,
                'hub_name': hub_name,
                'hub_address': hub_address,
                'return_date': return_date,
                'action': 'return_reminder'
            },
            send_push=True
        )
        
        logger.info(f"Sent return reminder for reservation {reservation_id}")
        return {'status': 'sent', 'reservation_id': reservation_id}
        
    except Exception as exc:
        logger.error(
            f"Failed to send return reminder for {reservation_id}: {str(exc)}",
            exc_info=True
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.send_overdue_notification',
    max_retries=3,
    default_retry_delay=60,
)
def send_overdue_notification(
    self, reservation_id, user_email, user_name, item_name,
    hub_name, days_overdue, expected_return_date
):
    """Send overdue item notification."""
    try:
        from users.notifications import notification_service
        from users.models import User
        
        # Get user
        user = User.objects.get(email=user_email)
        
        urgency = "URGENT: " if days_overdue >= 7 else ""
        
        # Create push notification
        notification_service.create_notification(
            recipient_id=str(user.id),
            notification_type='reminder',
            title=f"{urgency}Item Overdue",
            body=f"'{item_name}' is {days_overdue} day(s) overdue. Please return it to {hub_name} ASAP.",
            data={
                'reservation_id': reservation_id,
                'item_name': item_name,
                'hub_name': hub_name,
                'days_overdue': days_overdue,
                'expected_return_date': expected_return_date,
                'action': 'overdue',
                'urgent': days_overdue >= 7
            },
            send_push=True
        )
        
        logger.info(
            f"Sent overdue notification for reservation {reservation_id} "
            f"({days_overdue} days overdue)"
        )
        return {'status': 'sent', 'reservation_id': reservation_id, 'days_overdue': days_overdue}
        
    except Exception as exc:
        logger.error(
            f"Failed to send overdue notification for {reservation_id}: {str(exc)}",
            exc_info=True
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name='reservations.notify_stewards_overdue',
    max_retries=3,
    default_retry_delay=60,
)
def notify_stewards_overdue(
    self, reservation_id, hub_id, user_name, user_email,
    item_name, days_overdue
):
    """Notify hub stewards about overdue items."""
    try:
        from hubs.models import Hub
        from users.notifications import notification_service
        
        hub = Hub.objects.prefetch_related('stewards').get(id=hub_id)
        stewards = hub.stewards.all()
        
        if not stewards.exists():
            logger.warning(f"No stewards found for hub {hub_id}")
            return {'status': 'no_stewards', 'hub_id': hub_id}
        
        # Send push notification to each steward
        for steward in stewards:
            notification_service.create_notification(
                recipient_id=str(steward.id),
                notification_type='incident',
                title=f"Overdue Item Alert",
                body=f"'{item_name}' is {days_overdue} days overdue. Borrower: {user_name}",
                data={
                    'reservation_id': reservation_id,
                    'item_name': item_name,
                    'borrower_name': user_name,
                    'borrower_email': user_email,
                    'days_overdue': days_overdue,
                    'hub_id': hub_id,
                    'action': 'steward_alert'
                },
                send_push=True
            )
        
        logger.info(
            f"Notified {stewards.count()} stewards about overdue reservation {reservation_id}"
        )
        return {
            'status': 'sent',
            'reservation_id': reservation_id,
            'stewards_notified': stewards.count()
        }
        
    except Exception as exc:
        logger.error(
            f"Failed to notify stewards for reservation {reservation_id}: {str(exc)}",
            exc_info=True
        )
        raise self.retry(exc=exc)


# ============================================================================
# Utility Tasks
# ============================================================================

@shared_task(name='reservations.cleanup_old_reservations')
def cleanup_old_reservations():
    """
    Archive or clean up old completed/cancelled reservations.
    
    Runs: Weekly on Sunday at 2 AM
    """
    try:
        # Keep reservations for 90 days after completion
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_reservations = Reservation.objects.filter(
            Q(status=Reservation.Status.RETURNED) | Q(status=Reservation.Status.CANCELLED),
            updated_at__lt=cutoff_date
        )
        
        count = old_reservations.count()
        
        # In production, you might want to archive to a separate table
        # For now, we'll just log (not delete to preserve history)
        logger.info(f"Found {count} old reservations eligible for archival")
        
        return {
            'eligible_for_archival': count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_reservations: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(name='reservations.generate_reservation_report')
def generate_reservation_report():
    """
    Generate daily reservation statistics report.
    
    Runs: Daily at 11 PM
    """
    try:
        today = timezone.now().date()
        
        stats = {
            'date': today.isoformat(),
            'total_active': Reservation.objects.filter(
                status__in=[
                    Reservation.Status.PENDING,
                    Reservation.Status.CONFIRMED,
                    Reservation.Status.PICKED_UP
                ]
            ).count(),
            'created_today': Reservation.objects.filter(
                created_at__date=today
            ).count(),
            'picked_up_today': Reservation.objects.filter(
                status=Reservation.Status.PICKED_UP,
                updated_at__date=today
            ).count(),
            'returned_today': Reservation.objects.filter(
                status=Reservation.Status.RETURNED,
                actual_return_date=today
            ).count(),
            'overdue': Reservation.objects.filter(
                status=Reservation.Status.OVERDUE
            ).count(),
        }
        
        logger.info(f"Daily reservation report: {stats}")
        
        # In production, you might want to store this in a metrics database
        # or send to a monitoring service
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in generate_reservation_report: {str(e)}", exc_info=True)
        return {'error': str(e)}

@shared_task(
    bind=True,
    name='reservations.lift_expired_restrictions',
    max_retries=3,
    default_retry_delay=300,
)
def lift_expired_restrictions(self):
    """
    Automatically lift expired borrowing restrictions.
    
    This task:
    1. Finds all users with expired restrictions
    2. Lifts their restrictions
    3. Sends restoration notifications
    
    Runs: Daily via Celery Beat
    """
    try:
        from reservations.late_return_service import LateReturnService
        
        count = LateReturnService.check_and_lift_expired_restrictions()
        
        logger.info(f"Lifted {count} expired borrowing restrictions")
        
        return {
            'restrictions_lifted': count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in lift_expired_restrictions: {str(e)}", exc_info=True)
        self.retry(exc=e)


@shared_task(
    bind=True,
    name='reservations.send_restriction_reminders',
    max_retries=3,
    default_retry_delay=300,
)
def send_restriction_reminders(self):
    """
    Send reminders to users whose restrictions are ending soon.
    
    This task:
    1. Finds users with restrictions ending in the next 7 days
    2. Sends them reminder notifications
    
    Runs: Daily via Celery Beat
    """
    try:
        from reservations.late_return_service import LateReturnService
        
        count = LateReturnService.send_approaching_restriction_reminders()
        
        logger.info(f"Sent {count} restriction ending reminders")
        
        return {
            'reminders_sent': count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in send_restriction_reminders: {str(e)}", exc_info=True)
        self.retry(exc=e)