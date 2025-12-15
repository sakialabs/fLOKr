"""
Notification models for the fLOKr platform.

Handles push notifications, in-app notifications, and notification preferences.
"""
from django.db import models
from django.conf import settings
import uuid


class NotificationPreference(models.Model):
    """User notification preferences."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Push notification settings
    push_enabled = models.BooleanField(default=True)
    push_reservations = models.BooleanField(default=True)
    push_reminders = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_community = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)    # e.g., 08:00
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
    
    class Meta:
        db_table = 'notification_preferences'


class DeviceToken(models.Model):
    """Store device tokens for push notifications (FCM/APNS)."""
    
    class Platform(models.TextChoices):
        IOS = 'ios', 'iOS'
        ANDROID = 'android', 'Android'
        WEB = 'web', 'Web'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    device_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.token[:20]}..."
    
    class Meta:
        db_table = 'device_tokens'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]


class Notification(models.Model):
    """In-app notifications."""
    
    class Type(models.TextChoices):
        RESERVATION = 'reservation', 'Reservation'
        REMINDER = 'reminder', 'Reminder'
        MESSAGE = 'message', 'Message'
        COMMUNITY = 'community', 'Community'
        SYSTEM = 'system', 'System'
        INCIDENT = 'incident', 'Incident'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    # Optional data payload (JSON)
    data = models.JSONField(default=dict, blank=True)
    
    # Tracking
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification tracking
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.type} for {self.recipient.email}: {self.title}"
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['type']),
        ]
