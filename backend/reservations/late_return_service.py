"""
Late return restriction service.
Manages borrowing restrictions, grace periods, and automatic removal.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from users.notifications import send_notification

User = get_user_model()


class LateReturnService:
    """Service for managing late return restrictions."""
    
    # Configuration
    LATE_RETURN_THRESHOLD = 3  # Number of late returns before restriction
    RESTRICTION_DAYS = 30  # Days of restriction
    WARNING_THRESHOLD = 2  # Send warning after this many late returns
    GRACE_PERIOD_DAYS = 7  # Days before restriction to send warning
    
    @staticmethod
    def apply_late_return_penalty(user, reservation):
        """
        Apply penalty for late return.
        
        Args:
            user: User who returned late
            reservation: The late reservation
        """
        days_late = (reservation.actual_return_date - reservation.expected_return_date).days
        
        # Increment late return counter
        user.late_return_count += 1
        
        # Send warning notification
        if user.late_return_count == LateReturnService.WARNING_THRESHOLD:
            LateReturnService._send_warning_notification(user)
        
        # Apply restriction if threshold reached
        if user.late_return_count >= LateReturnService.LATE_RETURN_THRESHOLD:
            LateReturnService._apply_restriction(user)
        else:
            # Send late return notification
            send_notification(
                user=user,
                notification_type='late_return',
                title="Late return recorded",
                message=f"You returned {reservation.item.name} {days_late} day(s) late. Please try to return items on time to keep the community running smoothly.",
                data={
                    'reservation_id': str(reservation.id),
                    'days_late': days_late,
                    'late_return_count': user.late_return_count,
                    'threshold': LateReturnService.LATE_RETURN_THRESHOLD
                }
            )
        
        user.save()
    
    @staticmethod
    def _send_warning_notification(user):
        """Send warning notification before restriction."""
        send_notification(
            user=user,
            notification_type='restriction_warning',
            title="Borrowing privilege notice",
            message=f"You've had {user.late_return_count} late returns. One more late return will temporarily restrict your borrowing privileges. Please return items on time.",
            data={
                'late_return_count': user.late_return_count,
                'threshold': LateReturnService.LATE_RETURN_THRESHOLD
            }
        )
    
    @staticmethod
    def _apply_restriction(user):
        """Apply borrowing restriction."""
        restriction_end = timezone.now() + timedelta(days=LateReturnService.RESTRICTION_DAYS)
        user.borrowing_restricted_until = restriction_end
        user.save()
        
        send_notification(
            user=user,
            notification_type='borrowing_restricted',
            title="Borrowing privileges temporarily restricted",
            message=f"Due to {user.late_return_count} late returns, your borrowing privileges are restricted until {restriction_end.strftime('%B %d, %Y')}. You can still return current items. Restrictions will be automatically lifted on that date.",
            data={
                'late_return_count': user.late_return_count,
                'restriction_end': restriction_end.isoformat(),
                'restriction_days': LateReturnService.RESTRICTION_DAYS
            }
        )
    
    @staticmethod
    def lift_restriction(user, lifted_by=None, reason=None):
        """
        Manually lift a user's borrowing restriction.
        
        Args:
            user: User to lift restriction for
            lifted_by: Steward/admin who lifted it (optional)
            reason: Reason for lifting (optional)
        """
        if not user.borrowing_restricted_until:
            return False
        
        user.borrowing_restricted_until = None
        # Optionally reset late return count
        # user.late_return_count = 0
        user.save()
        
        send_notification(
            user=user,
            notification_type='restriction_lifted',
            title="Borrowing privileges restored",
            message="Your borrowing privileges have been restored. You can now make new reservations. Please remember to return items on time.",
            data={
                'lifted_by': lifted_by.get_full_name() if lifted_by else 'System',
                'reason': reason or 'Restriction period ended'
            }
        )
        
        return True
    
    @staticmethod
    def check_and_lift_expired_restrictions():
        """
        Check for expired restrictions and lift them automatically.
        Called by Celery task.
        
        Returns:
            Number of restrictions lifted
        """
        now = timezone.now()
        
        # Find users with expired restrictions
        restricted_users = User.objects.filter(
            borrowing_restricted_until__lte=now
        )
        
        count = 0
        for user in restricted_users:
            LateReturnService.lift_restriction(user, reason='Restriction period ended')
            count += 1
        
        return count
    
    @staticmethod
    def send_approaching_restriction_reminders():
        """
        Send reminders to users whose restrictions are ending soon.
        Called by Celery task.
        
        Returns:
            Number of reminders sent
        """
        now = timezone.now()
        grace_date = now + timedelta(days=LateReturnService.GRACE_PERIOD_DAYS)
        
        # Find users with restrictions ending in the grace period
        approaching_users = User.objects.filter(
            borrowing_restricted_until__gte=now,
            borrowing_restricted_until__lte=grace_date
        )
        
        count = 0
        for user in approaching_users:
            days_remaining = (user.borrowing_restricted_until - now).days
            
            send_notification(
                user=user,
                notification_type='restriction_ending',
                title="Your borrowing privileges will be restored soon",
                message=f"Your borrowing restriction will be lifted in {days_remaining} day(s). After that, you can make new reservations.",
                data={
                    'days_remaining': days_remaining,
                    'restriction_end': user.borrowing_restricted_until.isoformat()
                }
            )
            count += 1
        
        return count
    
    @staticmethod
    def get_restriction_status(user):
        """
        Get detailed restriction status for a user.
        
        Returns:
            dict with restriction info
        """
        is_restricted = user.borrowing_restricted_until and user.borrowing_restricted_until > timezone.now()
        
        status = {
            'is_restricted': is_restricted,
            'late_return_count': user.late_return_count,
            'threshold': LateReturnService.LATE_RETURN_THRESHOLD,
            'restriction_end': user.borrowing_restricted_until.isoformat() if is_restricted else None,
            'can_borrow': not is_restricted
        }
        
        if is_restricted:
            days_remaining = (user.borrowing_restricted_until - timezone.now()).days
            status['days_remaining'] = days_remaining
            status['message'] = f"Your borrowing privileges are restricted for {days_remaining} more day(s)."
        elif user.late_return_count > 0:
            remaining_before_restriction = LateReturnService.LATE_RETURN_THRESHOLD - user.late_return_count
            status['message'] = f"You have {user.late_return_count} late return(s). {remaining_before_restriction} more will result in temporary restriction."
        else:
            status['message'] = "Your borrowing privileges are in good standing."
        
        return status
