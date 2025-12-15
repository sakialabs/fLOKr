from django.db import models
from django.conf import settings
import uuid


class Badge(models.Model):
    """Model for achievement badges."""
    
    class Category(models.TextChoices):
        CONTRIBUTION = 'contribution', 'Contribution'
        MENTORSHIP = 'mentorship', 'Mentorship'
        COMMUNITY = 'community', 'Community'
        MILESTONE = 'milestone', 'Milestone'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(blank=True)
    criteria = models.JSONField(default=dict)
    category = models.CharField(max_length=20, choices=Category.choices)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'badges'
        ordering = ['category', 'name']


class UserBadge(models.Model):
    """Model for tracking user badge awards."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    awarded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']


class Feedback(models.Model):
    """Model for user feedback and incident reports."""
    
    class Type(models.TextChoices):
        POSITIVE = 'positive', 'Positive'
        NEGATIVE = 'negative', 'Negative'
        INCIDENT = 'incident', 'Incident'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        REVIEWED = 'reviewed', 'Reviewed'
        RESOLVED = 'resolved', 'Resolved'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_submitted')
    item = models.ForeignKey('inventory.InventoryItem', on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    reservation = models.ForeignKey('reservations.Reservation', on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    type = models.CharField(max_length=20, choices=Type.choices)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type} feedback from {self.user.email}"
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']


class MentorshipConnection(models.Model):
    """Model for mentor-mentee connections."""
    
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        DECLINED = 'declined', 'Declined'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentoring')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentored_by')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    feedback_mentor = models.TextField(blank=True)
    feedback_mentee = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mentor.email} mentoring {self.mentee.email}"
    
    class Meta:
        db_table = 'mentorship_connections'
        ordering = ['-created_at']


class Message(models.Model):
    """Model for in-app messages between mentors and mentees."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(MentorshipConnection, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    translated_content = models.JSONField(default=dict, blank=True)
    read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
