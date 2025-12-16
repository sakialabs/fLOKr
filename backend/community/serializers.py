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
        fields = ['id', 'name', 'description', 'icon_url', 'criteria', 'category', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserBadgeSerializer(serializers.ModelSerializer):
    """Serializer for UserBadge model with badge details."""
    badge = BadgeSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'user_name', 'badge', 'awarded_at']
        read_only_fields = ['id', 'awarded_at']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_name', 'item', 'item_name', 'reservation',
            'type', 'rating', 'comment', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
