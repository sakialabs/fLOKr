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
    
    # Incident reporting fields
    incident_report_count = models.IntegerField(default=0)
    is_flagged = models.BooleanField(default=False)
    flagged_at = models.DateTimeField(null=True, blank=True)
    
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

class InventoryTransfer(models.Model):
    """Model for tracking inventory transfers between hubs."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_TRANSIT = 'in_transit', 'In Transit'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transfers')
    from_hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='transfers_out')
    to_hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='transfers_in')
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Tracking
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='transfers_initiated')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_approved')
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_completed')
    
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.item.name}: {self.from_hub.name} → {self.to_hub.name} ({self.quantity})"
    
    class Meta:
        db_table = 'inventory_transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_hub', 'status']),
            models.Index(fields=['to_hub', 'status']),
            models.Index(fields=['status']),
        ]