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
