from django.db import models
from django.conf import settings
import uuid


class InventoryItem(models.Model):
    """Model for inventory items available for borrowing."""
    
    class Condition(models.TextChoices):
        NEW = 'new', 'New'
        EXCELLENT = 'excellent', 'Excellent'
        GOOD = 'good', 'Good'
        FAIR = 'fair', 'Fair'
        POOR = 'poor', 'Poor'
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        DAMAGED = 'damaged', 'Damaged'
        RESERVED = 'reserved', 'Reserved'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    images = models.JSONField(default=list, blank=True)
    quantity_total = models.IntegerField(default=1)
    quantity_available = models.IntegerField(default=1)
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='donated_items')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.hub.name})"
    
    class Meta:
        db_table = 'inventory_items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['hub', 'status']),
        ]
