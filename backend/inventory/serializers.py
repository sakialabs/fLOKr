from rest_framework import serializers
from .models import InventoryItem
from hubs.serializers import HubListSerializer
from users.serializers import UserProfileSerializer


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model."""
    hub_details = HubListSerializer(source='hub', read_only=True)
    donor_details = UserProfileSerializer(source='donor', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'hub', 'hub_details', 'name', 'description', 'category',
            'tags', 'condition', 'images', 'quantity_total', 'quantity_available',
            'donor', 'donor_details', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate quantity_available <= quantity_total."""
        quantity_total = data.get('quantity_total', getattr(self.instance, 'quantity_total', 0))
        quantity_available = data.get('quantity_available', getattr(self.instance, 'quantity_available', 0))
        
        if quantity_available > quantity_total:
            raise serializers.ValidationError({
                'quantity_available': 'Available quantity cannot exceed total quantity'
            })
        
        return data


class InventoryItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for item lists."""
    hub_name = serializers.CharField(source='hub.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'condition', 'quantity_available',
            'hub_name', 'primary_image', 'status', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get first image if available."""
        return obj.images[0] if obj.images else None


class InventoryItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating inventory items."""
    
    class Meta:
        model = InventoryItem
        fields = [
            'hub', 'name', 'description', 'category', 'tags', 'condition',
            'images', 'quantity_total', 'quantity_available', 'donor'
        ]
    
    def create(self, validated_data):
        # Set donor to current user if not provided
        if 'donor' not in validated_data:
            validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)
