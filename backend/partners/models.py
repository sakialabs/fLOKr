from django.db import models
import uuid


class Partner(models.Model):
    """Model for partner organizations."""
    
    class SubscriptionTier(models.TextChoices):
        BASIC = 'basic', 'Basic'
        PREMIUM = 'premium', 'Premium'
        ENTERPRISE = 'enterprise', 'Enterprise'
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        SUSPENDED = 'suspended', 'Suspended'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    subscription_tier = models.CharField(max_length=20, choices=SubscriptionTier.choices, default=SubscriptionTier.BASIC)
    sponsored_categories = models.JSONField(default=list, blank=True)
    subscription_start = models.DateField()
    subscription_end = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.organization_name
    
    class Meta:
        db_table = 'partners'
        ordering = ['organization_name']


class DemandForecast(models.Model):
    """Model for storing demand forecasts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hub = models.ForeignKey('hubs.Hub', on_delete=models.CASCADE, related_name='forecasts')
    category = models.CharField(max_length=100)
    forecast_date = models.DateField()
    predicted_demand = models.IntegerField()
    actual_demand = models.IntegerField(null=True, blank=True)
    confidence_score = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hub.name} - {self.category} - {self.forecast_date}"
    
    class Meta:
        db_table = 'demand_forecasts'
        ordering = ['-forecast_date']
        unique_together = ['hub', 'category', 'forecast_date']
