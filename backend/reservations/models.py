from django.db import models
from django.conf import settings
import uuid


class Reservation(models.Model):
    """Model for item reservations."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PICKED_UP = 'picked_up', 'Picked Up'
        RETURNED = 'returned', 'Returned'
        CANCELLED = 'cancelled', 'Cancelled'
        OVERDUE = 'overdue', 'Overdue'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    item = models.ForeignKey('inventory.InventoryItem', on_delete=models.CASCADE, related_name='reservations')
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='reservations')
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reservation_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    extension_requested = models.BooleanField(default=False)
    extension_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.item.name} ({self.status})"
    
    class Meta:
        db_table = 'reservations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['hub', 'status']),
        ]
