"""
Serializers for partner app models
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    """Serializer for Partner model."""
    
    subscription_status = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    sponsored_category_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Partner
        fields = [
            'id', 'organization_name', 'contact_email', 'subscription_tier',
            'sponsored_categories', 'subscription_start', 'subscription_end',
            'status', 'subscription_status', 'days_remaining', 'is_active',
            'sponsored_category_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def get_subscription_status(self, obj):
        """Get human-readable subscription status"""
        today = timezone.now().date()
        
        if obj.subscription_end < today:
            return 'expired'
        elif obj.subscription_end <= today + timezone.timedelta(days=7):
            return 'expiring_soon'
        elif obj.status == 'suspended':
            return 'suspended'
        else:
            return 'active'
    
    def get_days_remaining(self, obj):
        """Get days remaining in subscription"""
        today = timezone.now().date()
        delta = obj.subscription_end - today
        return max(delta.days, 0)
    
    def get_is_active(self, obj):
        """Check if partner subscription is currently active"""
        today = timezone.now().date()
        return (
            obj.status == 'active' and
            obj.subscription_start <= today <= obj.subscription_end
        )
    
    def get_sponsored_category_count(self, obj):
        """Get count of sponsored categories"""
        return len(obj.sponsored_categories) if obj.sponsored_categories else 0
    
    def validate_subscription_end(self, value):
        """Ensure subscription end is after start"""
        if 'subscription_start' in self.initial_data:
            start = self.initial_data['subscription_start']
            if isinstance(start, str):
                from datetime import datetime
                start = datetime.fromisoformat(start).date()
            
            if value <= start:
                raise serializers.ValidationError(
                    "Subscription end date must be after start date"
                )
        
        return value
    
    def validate_subscription_tier(self, value):
        """Validate subscription tier and related constraints"""
        valid_tiers = ['basic', 'premium', 'enterprise']
        if value not in valid_tiers:
            raise serializers.ValidationError(
                f"Invalid subscription tier. Must be one of: {', '.join(valid_tiers)}"
            )
        return value
    
    def validate_sponsored_categories(self, value):
        """Validate sponsored categories based on subscription tier"""
        # Get subscription tier from initial data or instance
        tier = self.initial_data.get('subscription_tier')
        if not tier and self.instance:
            tier = self.instance.subscription_tier
        
        # Enforce category limits by tier
        max_categories = {
            'basic': 2,
            'premium': 5,
            'enterprise': 999  # Unlimited
        }
        
        if tier and len(value) > max_categories.get(tier, 0):
            raise serializers.ValidationError(
                f"{tier.capitalize()} tier allows max {max_categories[tier]} sponsored categories"
            )
        
        return value
    
    def create(self, validated_data):
        """Create partner with automatic status setting"""
        # Set status based on subscription dates
        today = timezone.now().date()
        start = validated_data.get('subscription_start')
        end = validated_data.get('subscription_end')
        
        if start <= today <= end:
            validated_data['status'] = 'active'
        elif end < today:
            validated_data['status'] = 'expired'
        else:
            validated_data['status'] = 'active'  # Future start date
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update partner and refresh status"""
        partner = super().update(instance, validated_data)
        
        # Update status based on current subscription dates
        today = timezone.now().date()
        if partner.subscription_end < today:
            partner.status = 'expired'
            partner.save(update_fields=['status'])
        
        return partner


class PartnerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for partner listings"""
    
    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Partner
        fields = [
            'id', 'organization_name', 'subscription_tier', 'status',
            'is_active', 'days_remaining', 'subscription_end'
        ]
    
    def get_is_active(self, obj):
        """Check if partner subscription is currently active"""
        today = timezone.now().date()
        return (
            obj.status == 'active' and
            obj.subscription_start <= today <= obj.subscription_end
        )
    
    def get_days_remaining(self, obj):
        """Get days remaining in subscription"""
        today = timezone.now().date()
        delta = obj.subscription_end - today
        return max(delta.days, 0)


class PartnerAnalyticsSerializer(serializers.Serializer):
    """Serializer for partner analytics data"""
    
    partner_id = serializers.UUIDField()
    organization_name = serializers.CharField()
    subscription_tier = serializers.CharField()
    
    # Demand analytics
    total_category_demand = serializers.IntegerField()
    sponsored_category_views = serializers.IntegerField()
    top_categories = serializers.ListField()
    
    # Trend data
    weekly_trend = serializers.DictField()
    monthly_trend = serializers.DictField()
    
    # Privacy-safe aggregated data
    unique_hub_count = serializers.IntegerField()
    avg_category_demand = serializers.FloatField()
    
    # Metadata
    data_period_start = serializers.DateField()
    data_period_end = serializers.DateField()
    last_updated = serializers.DateTimeField()
