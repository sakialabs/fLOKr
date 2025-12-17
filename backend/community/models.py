from django.db import models
from django.conf import settings
import uuid


class Badge(models.Model):
    """Model for achievement badges - meaningful, not cringe."""
    
    class Category(models.TextChoices):
        ARRIVAL = 'arrival', 'Arrival & Belonging'
        CONTRIBUTION = 'contribution', 'Contribution & Care'
        COMMUNITY = 'community', 'Community Energy'
        TRUST = 'trust', 'Steward & Trust'
        MILESTONE = 'milestone', 'Milestone'  # Keep for backward compatibility
        MENTORSHIP = 'mentorship', 'Mentorship'  # Keep for backward compatibility
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True)
    icon = models.CharField(max_length=50, default='🏆')  # Emoji icon
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    criteria = models.JSONField(default=dict)
    category = models.CharField(max_length=20, choices=Category.choices)
    
    # Soft privileges (not power)
    unlocks_feature = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional feature this badge unlocks"
    )
    
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name
    
    class Meta:
        db_table = 'badges'
        ordering = ['category', 'sort_order', 'name']


class UserBadge(models.Model):
    """Model for tracking user badge awards - quiet recognition."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_reason = models.TextField(blank=True, help_text="Optional Ori message")
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
    
    def mark_viewed(self):
        """Mark badge as viewed by user"""
        if not self.viewed_at:
            from django.utils import timezone
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed_at'])
    
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
    
    # Resolution tracking
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_reviewed')
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
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


class UserLevel(models.Model):
    """
    User progression levels - status signals, not ranks
    Tied to birds and migration subtly
    """
    
    class Level(models.TextChoices):
        NEWCOMER = 'newcomer', 'Newcomer'
        NESTING = 'nesting', 'Nesting'
        GROUNDED = 'grounded', 'Grounded'
        TRUSTED_WING = 'trusted_wing', 'Trusted Wing'
        FLOCK_ANCHOR = 'flock_anchor', 'Flock Anchor'
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='level',
        primary_key=True
    )
    
    current_level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.NEWCOMER
    )
    
    # Progress metrics (not competitive)
    total_contributions = models.IntegerField(default=0)
    total_reservations = models.IntegerField(default=0)
    total_connections = models.IntegerField(default=0)
    
    # Milestone tracking
    last_level_change = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.get_current_level_display()}"
    
    def check_level_up(self):
        """
        Check if user should level up based on activity
        Progression is gentle, not aggressive
        """
        from django.utils import timezone
        
        total_activity = (
            self.total_contributions +
            self.total_reservations +
            self.total_connections
        )
        
        # Gentle progression thresholds
        if total_activity >= 50 and self.current_level == self.Level.NEWCOMER:
            self.current_level = self.Level.NESTING
            self.last_level_change = timezone.now()
            self.save()
            return True
        elif total_activity >= 100 and self.current_level == self.Level.NESTING:
            self.current_level = self.Level.GROUNDED
            self.last_level_change = timezone.now()
            self.save()
            return True
        elif total_activity >= 200 and self.current_level == self.Level.GROUNDED:
            self.current_level = self.Level.TRUSTED_WING
            self.last_level_change = timezone.now()
            self.save()
            return True
        elif total_activity >= 500 and self.current_level == self.Level.TRUSTED_WING:
            self.current_level = self.Level.FLOCK_ANCHOR
            self.last_level_change = timezone.now()
            self.save()
            return True
        
        return False
    
    class Meta:
        db_table = 'user_levels'
