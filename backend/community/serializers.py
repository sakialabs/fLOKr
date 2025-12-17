"""
Serializers for community app models
"""
from rest_framework import serializers
from .models import Badge, UserBadge, Feedback, MentorshipConnection, Message
from users.serializers import UserProfileSerializer


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for Badge model."""
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'icon_url', 'color',
            'criteria', 'category', 'unlocks_feature', 'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserBadgeSerializer(serializers.ModelSerializer):
    """Serializer for UserBadge model with badge details."""
    badge = BadgeSerializer(read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'user_id', 'user_name', 'badge', 'awarded_at', 'awarded_reason', 'viewed_at']
        read_only_fields = ['id', 'awarded_at']


class UserLevelSerializer(serializers.Serializer):
    """Serializer for UserLevel model."""
    current_level = serializers.CharField()
    current_level_display = serializers.SerializerMethodField()
    total_contributions = serializers.IntegerField()
    total_reservations = serializers.IntegerField()
    total_connections = serializers.IntegerField()
    total_activity = serializers.SerializerMethodField()
    last_level_change = serializers.DateTimeField()
    
    def get_current_level_display(self, obj):
        return obj.get_current_level_display()
    
    def get_total_activity(self, obj):
        return obj.total_contributions + obj.total_reservations + obj.total_connections


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model."""
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_is_flagged = serializers.BooleanField(source='item.is_flagged', read_only=True)
    item_incident_count = serializers.IntegerField(source='item.incident_report_count', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_id', 'user_name', 'item', 'item_name', 'item_is_flagged', 
            'item_incident_count', 'reservation', 'type', 'rating', 'comment', 
            'status', 'reviewed_by', 'reviewed_by_name', 'resolution_notes', 
            'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'connection', 'sender', 'sender_name', 'content', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']


class MentorshipConnectionSerializer(serializers.ModelSerializer):
    """Serializer for MentorshipConnection model."""
    mentor = UserProfileSerializer(read_only=True)
    mentee = UserProfileSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MentorshipConnection
        fields = [
            'id', 'mentor', 'mentee', 'status', 'start_date', 'end_date',
            'feedback_mentor', 'feedback_mentee', 'messages', 'message_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class MentorshipConnectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for mentorship lists."""
    mentor_name = serializers.CharField(source='mentor.get_full_name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.get_full_name', read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MentorshipConnection
        fields = [
            'id', 'mentor_name', 'mentee_name', 'status',
            'start_date', 'unread_count', 'created_at'
        ]
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(read=False).exclude(sender=request.user).count()
        return 0
