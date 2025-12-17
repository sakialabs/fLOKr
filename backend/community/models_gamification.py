"""
Gamification Models
Badge system that enhances dignity, not dopamine
"""
from django.db import models
from django.utils import timezone
from users.models import User
import uuid


class Badge(models.Model):
    """
    Badge definitions - meaningful achievements, not cringe
    Categories align with flock & migration metaphor
    """
    
    class Category(models.TextChoices):
        ARRIVAL = 'arrival', 'Arrival & Belonging'
        CONTRIBUTION = 'contribution', 'Contribution & Care'
        COMMUNITY = 'community', 'Community Energy'
        TRUST = 'trust', 'Steward & Trust'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    
    # Criteria for earning (stored as JSON for flexibility)
    criteria = models.JSONField(
        help_text="Criteria for earning this badge (e.g., {'reservations_count': 1})"
    )
    
    # Icon and visual
    icon = models.CharField(max_length=50, default='🏆')
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    
    # Soft privileges (not power)
    unlocks_feature = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional feature this badge unlocks (e.g., 'priority_reservation')"
    )
    
    # Metadata
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """
    User badge awards - quiet recognition, not leaderboards
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    
    # Award details
    awarded_at = models.DateTimeField(default=timezone.now)
    awarded_reason = models.TextField(blank=True, help_text="Optional Ori message")
    
    # Acknowledgment
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']
        indexes = [
            models.Index(fields=['user', 'awarded_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
    
    def mark_viewed(self):
        """Mark badge as viewed by user"""
        if not self.viewed_at:
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed_at'])


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
        User,
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
    last_level_change = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['current_level']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_current_level_display()}"
    
    def check_level_up(self):
        """
        Check if user should level up based on activity
        Progression is gentle, not aggressive
        """
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


class SeasonalMigration(models.Model):
    """
    Seasonal collective goals - flock energy
    Progress is collective, rewards are collective
    """
    
    class Season(models.TextChoices):
        WINTER = 'winter', 'Winter Warmth Drive'
        SPRING = 'spring', 'Spring Reset'
        SUMMER = 'summer', 'Back-to-School Support'
        FALL = 'fall', 'Fall Harvest'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.CharField(max_length=20, choices=Season.choices)
    year = models.IntegerField()
    
    # Goal details
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Progress
    goal_target = models.IntegerField(help_text="Target number (items donated, connections made, etc.)")
    current_progress = models.IntegerField(default=0)
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['season', 'year']
        ordering = ['-year', '-start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.get_season_display()} {self.year}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.goal_target == 0:
            return 0
        return min(100, int((self.current_progress / self.goal_target) * 100))
    
    def update_progress(self, increment=1):
        """Update progress and check for completion"""
        self.current_progress += increment
        
        if self.current_progress >= self.goal_target and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        
        self.save()
