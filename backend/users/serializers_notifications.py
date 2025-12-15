"""
Serializers for notification-related models.
"""
from rest_framework import serializers
from users.models_notifications import Notification, NotificationPreference, DeviceToken


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'body', 'data',
            'read', 'read_at', 'push_sent', 'created_at'
        ]
        read_only_fields = ['id', 'push_sent', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'push_enabled', 'push_reservations', 'push_reminders',
            'push_messages', 'push_community',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]
    
    def validate(self, data):
        """Validate quiet hours."""
        if data.get('quiet_hours_enabled'):
            if not data.get('quiet_hours_start') or not data.get('quiet_hours_end'):
                raise serializers.ValidationError(
                    "Both quiet_hours_start and quiet_hours_end are required when quiet hours are enabled"
                )
        return data


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for DeviceToken model."""
    
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'device_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']
    
    def validate_platform(self, value):
        """Validate platform choice."""
        if value not in ['ios', 'android', 'web']:
            raise serializers.ValidationError("Platform must be ios, android, or web")
        return value


class DeviceTokenCreateSerializer(serializers.Serializer):
    """Serializer for registering a device token."""
    
    token = serializers.CharField(max_length=500, required=True)
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'], required=True)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
