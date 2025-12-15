"""
Notification service for sending push notifications via Firebase Cloud Messaging.

This module handles:
- Push notification delivery to iOS/Android/Web
- In-app notification creation
- Notification preferences checking
- Quiet hours enforcement
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, time as datetime_time
from django.utils import timezone
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

# Firebase Admin SDK (optional - install with: pip install firebase-admin)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not installed. Push notifications will be logged only.")


class NotificationService:
    """Service for managing and sending notifications."""
    
    def __init__(self):
        """Initialize Firebase if available."""
        self.firebase_initialized = False
        
        if FIREBASE_AVAILABLE and hasattr(settings, 'FIREBASE_CREDENTIALS_PATH'):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                self.firebase_initialized = True
                logger.info("Firebase initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
    
    def create_notification(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        send_push: bool = True
    ) -> 'Notification':
        """
        Create an in-app notification and optionally send push notification.
        
        Args:
            recipient_id: User ID to send notification to
            notification_type: Type of notification (reservation, reminder, etc.)
            title: Notification title
            body: Notification body text
            data: Optional data payload
            send_push: Whether to send push notification
        
        Returns:
            Created Notification instance
        """
        from users.models_notifications import Notification
        from users.models import User
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            logger.error(f"User {recipient_id} not found")
            raise
        
        # Create in-app notification
        notification = Notification.objects.create(
            recipient=recipient,
            type=notification_type,
            title=title,
            body=body,
            data=data or {}
        )
        
        logger.info(f"Created notification {notification.id} for {recipient.email}")
        
        # Send push notification if requested
        if send_push:
            self.send_push_notification(notification)
        
        return notification
    
    def send_push_notification(self, notification: 'Notification') -> Dict[str, Any]:
        """
        Send push notification to user's devices.
        
        Args:
            notification: Notification instance to send
        
        Returns:
            Dict with success/failure counts
        """
        from users.models_notifications import DeviceToken, NotificationPreference
        
        recipient = notification.recipient
        
        # Check if user has push notifications enabled
        try:
            prefs = recipient.notification_preferences
            if not prefs.push_enabled:
                logger.info(f"Push notifications disabled for {recipient.email}")
                return {'sent': 0, 'failed': 0, 'reason': 'disabled'}
            
            # Check notification type preferences
            if notification.type == 'reservation' and not prefs.push_reservations:
                return {'sent': 0, 'failed': 0, 'reason': 'type_disabled'}
            if notification.type == 'reminder' and not prefs.push_reminders:
                return {'sent': 0, 'failed': 0, 'reason': 'type_disabled'}
            if notification.type == 'message' and not prefs.push_messages:
                return {'sent': 0, 'failed': 0, 'reason': 'type_disabled'}
            if notification.type == 'community' and not prefs.push_community:
                return {'sent': 0, 'failed': 0, 'reason': 'type_disabled'}
            
            # Check quiet hours
            if prefs.quiet_hours_enabled and self._is_quiet_hours(prefs):
                logger.info(f"Quiet hours active for {recipient.email}")
                return {'sent': 0, 'failed': 0, 'reason': 'quiet_hours'}
                
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            NotificationPreference.objects.create(user=recipient)
        
        # Get active device tokens
        device_tokens = DeviceToken.objects.filter(
            user=recipient,
            is_active=True
        )
        
        if not device_tokens.exists():
            logger.info(f"No active device tokens for {recipient.email}")
            return {'sent': 0, 'failed': 0, 'reason': 'no_tokens'}
        
        # Send to each device
        results = {
            'sent': 0,
            'failed': 0,
            'tokens_sent': [],
            'tokens_failed': []
        }
        
        for device in device_tokens:
            try:
                success = self._send_to_device(device, notification)
                if success:
                    results['sent'] += 1
                    results['tokens_sent'].append(str(device.id))
                    device.last_used_at = timezone.now()
                    device.save(update_fields=['last_used_at'])
                else:
                    results['failed'] += 1
                    results['tokens_failed'].append(str(device.id))
            except Exception as e:
                logger.error(f"Failed to send to device {device.id}: {e}")
                results['failed'] += 1
                results['tokens_failed'].append(str(device.id))
        
        # Update notification
        if results['sent'] > 0:
            notification.push_sent = True
            notification.push_sent_at = timezone.now()
            notification.save(update_fields=['push_sent', 'push_sent_at'])
        
        logger.info(
            f"Push notification {notification.id}: "
            f"{results['sent']} sent, {results['failed']} failed"
        )
        
        return results
    
    def _send_to_device(self, device: 'DeviceToken', notification: 'Notification') -> bool:
        """
        Send push notification to a specific device.
        
        Args:
            device: DeviceToken instance
            notification: Notification to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.firebase_initialized:
            # Log instead of sending (for development/testing)
            logger.info(
                f"[MOCK PUSH] To: {device.user.email} ({device.platform})\n"
                f"Title: {notification.title}\n"
                f"Body: {notification.body}\n"
                f"Data: {notification.data}"
            )
            return True
        
        try:
            # Build FCM message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body,
                ),
                data={
                    'notification_id': str(notification.id),
                    'type': notification.type,
                    **notification.data
                },
                token=device.token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='flokr_notifications'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # Send message
            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return True
            
        except messaging.UnregisteredError:
            # Token is invalid, deactivate it
            logger.warning(f"Invalid token for device {device.id}, deactivating")
            device.is_active = False
            device.save(update_fields=['is_active'])
            return False
            
        except Exception as e:
            logger.error(f"Error sending to device {device.id}: {e}")
            return False
    
    def _is_quiet_hours(self, prefs: 'NotificationPreference') -> bool:
        """Check if current time is within quiet hours."""
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False
        
        now = timezone.localtime().time()
        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            return now >= start or now <= end
        else:
            return start <= now <= end
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security check)
        
        Returns:
            True if marked as read, False if not found or unauthorized
        """
        from users.models_notifications import Notification
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient_id=user_id
            )
            
            if not notification.read:
                notification.read = True
                notification.read_at = timezone.now()
                notification.save(update_fields=['read', 'read_at'])
                logger.info(f"Marked notification {notification_id} as read")
            
            return True
            
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all unread notifications as read for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Number of notifications marked as read
        """
        from users.models_notifications import Notification
        
        count = Notification.objects.filter(
            recipient_id=user_id,
            read=False
        ).update(
            read=True,
            read_at=timezone.now()
        )
        
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user."""
        from users.models_notifications import Notification
        
        return Notification.objects.filter(
            recipient_id=user_id,
            read=False
        ).count()
    
    def register_device(
        self,
        user_id: str,
        token: str,
        platform: str,
        device_name: str = ''
    ) -> 'DeviceToken':
        """
        Register a device token for push notifications.
        
        Args:
            user_id: User ID
            token: FCM/APNS token
            platform: Platform (ios, android, web)
            device_name: Optional device name
        
        Returns:
            DeviceToken instance
        """
        from users.models_notifications import DeviceToken
        from users.models import User
        
        user = User.objects.get(id=user_id)
        
        # Check if token already exists
        device, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': user,
                'platform': platform,
                'device_name': device_name,
                'is_active': True,
                'last_used_at': timezone.now()
            }
        )
        
        if created:
            logger.info(f"Registered new device for {user.email}: {platform}")
        else:
            logger.info(f"Updated existing device for {user.email}: {platform}")
        
        return device
    
    def unregister_device(self, token: str) -> bool:
        """
        Unregister a device token.
        
        Args:
            token: FCM/APNS token
        
        Returns:
            True if unregistered, False if not found
        """
        from users.models_notifications import DeviceToken
        
        try:
            device = DeviceToken.objects.get(token=token)
            device.is_active = False
            device.save(update_fields=['is_active'])
            logger.info(f"Unregistered device {device.id}")
            return True
        except DeviceToken.DoesNotExist:
            logger.warning(f"Device token not found: {token[:20]}...")
            return False


# Global notification service instance
notification_service = NotificationService()
