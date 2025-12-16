from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings
import uuid


class Hub(models.Model):
    """Model for physical community hubs."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        MAINTENANCE = 'maintenance', 'Maintenance'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = gis_models.PointField(geography=True)
    operating_hours = models.JSONField(default=dict)
    stewards = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='managed_hubs', blank=True)
    capacity = models.IntegerField(default=100)
    current_inventory_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'hubs'
        ordering = ['name']


class Event(models.Model):
    """Model for hub events and community gatherings."""
    
    class EventType(models.TextChoices):
        COMMUNITY_DINNER = 'community_dinner', 'Community Dinner'
        WORKSHOP = 'workshop', 'Workshop'
        MEETING = 'meeting', 'Meeting'
        CELEBRATION = 'celebration', 'Celebration'
        VOLUNTEER = 'volunteer', 'Volunteer Opportunity'
        OTHER = 'other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=30, choices=EventType.choices, default=EventType.OTHER)
    event_date = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    max_participants = models.IntegerField(null=True, blank=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} at {self.hub.name}"
    
    class Meta:
        db_table = 'hub_events'
        ordering = ['event_date']


class Announcement(models.Model):
    """Model for hub announcements and updates."""
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='authored_announcements')
    active_until = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.hub.name}"
    
    class Meta:
        db_table = 'hub_announcements'
        ordering = ['-created_at']
