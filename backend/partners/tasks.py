"""
Celery tasks for partner subscription management.
Handles automatic expiration and renewal reminders.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def expire_partner_subscriptions():
    """
    Check and expire partner subscriptions daily.
    Removes sponsored categories from expired partners.
    """
    from partners.models import Partner
    
    today = timezone.now().date()
    
    # Find partners that expired today
    expired_partners = Partner.objects.filter(
        status='active',
        subscription_end__lt=today
    )
    
    count = 0
    for partner in expired_partners:
        # Update status
        partner.status = 'expired'
        
        # Clear sponsored categories
        partner.sponsored_categories = []
        
        partner.save(update_fields=['status', 'sponsored_categories'])
        
        logger.info(
            f"Expired partner subscription: {partner.organization_name} "
            f"(ID: {partner.id})"
        )
        
        count += 1
    
    logger.info(f"Expired {count} partner subscription(s)")
    return f"Expired {count} partner subscription(s)"


@shared_task
def send_expiration_reminders():
    """
    Send renewal reminders to partners expiring in 7 and 30 days.
    """
    from partners.models import Partner
    from users.notifications import NotificationService
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    today = timezone.now().date()
    
    # 7-day warning
    seven_days = today + timedelta(days=7)
    partners_7day = Partner.objects.filter(
        status='active',
        subscription_end=seven_days
    )
    
    # 30-day warning
    thirty_days = today + timedelta(days=30)
    partners_30day = Partner.objects.filter(
        status='active',
        subscription_end=thirty_days
    )
    
    # Send notifications to admins
    admins = User.objects.filter(role='admin')
    
    for partner in partners_7day:
        logger.info(
            f"Partner subscription expiring in 7 days: {partner.organization_name}"
        )
        for admin in admins:
            NotificationService.send_notification(
                user=admin,
                notification_type='partner_renewal',
                title='Partner Subscription Expiring Soon',
                message=f"{partner.organization_name}'s subscription expires in 7 days",
                data={'partner_id': str(partner.id), 'days_remaining': 7}
            )
    
    for partner in partners_30day:
        logger.info(
            f"Partner subscription expiring in 30 days: {partner.organization_name}"
        )
        for admin in admins:
            NotificationService.send_notification(
                user=admin,
                notification_type='partner_renewal',
                title='Partner Subscription Renewal Notice',
                message=f"{partner.organization_name}'s subscription expires in 30 days",
                data={'partner_id': str(partner.id), 'days_remaining': 30}
            )
    
    total = partners_7day.count() + partners_30day.count()
    return f"Sent renewal reminders for {total} partner(s)"


@shared_task
def cleanup_expired_partner_data():
    """
    Clean up data for partners that have been expired for >90 days.
    Maintains data retention policy while preserving analytics.
    """
    from partners.models import Partner
    
    today = timezone.now().date()
    ninety_days_ago = today - timedelta(days=90)
    
    # Find partners expired for more than 90 days
    long_expired = Partner.objects.filter(
        status='expired',
        subscription_end__lt=ninety_days_ago
    )
    
    count = 0
    for partner in long_expired:
        # Archive partner data before deletion (optional)
        logger.info(
            f"Partner subscription expired >90 days ago: {partner.organization_name} "
            f"(Last active: {partner.subscription_end})"
        )
        
        # Could archive to separate table or export data here
        # For now, just log
        count += 1
    
    logger.info(f"Found {count} partner(s) with expired subscriptions >90 days old")
    return f"Found {count} long-expired partner(s)"
