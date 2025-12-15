from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Hub
from users.serializers import UserProfileSerializer


class HubSerializer(serializers.ModelSerializer):
    """Serializer for Hub model."""
    stewards = UserProfileSerializer(many=True, read_only=True)
    steward_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Hub
        fields = [
            'id', 'name', 'address', 'location', 'operating_hours',
            'stewards', 'steward_ids', 'capacity', 'current_inventory_count',
            'status', 'distance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_inventory_count', 'created_at', 'updated_at']
    
    def get_distance(self, obj):
        """Get distance from user location if available in context."""
        return getattr(obj, 'distance', None)
    
    def create(self, validated_data):
        steward_ids = validated_data.pop('steward_ids', [])
        hub = Hub.objects.create(**validated_data)
        if steward_ids:
            hub.stewards.set(steward_ids)
        return hub
    
    def update(self, instance, validated_data):
        steward_ids = validated_data.pop('steward_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if steward_ids is not None:
            instance.stewards.set(steward_ids)
        return instance


class HubListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for hub lists."""
    steward_count = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Hub
        fields = [
            'id', 'name', 'address', 'location', 'status',
            'current_inventory_count', 'capacity', 'steward_count', 'distance'
        ]
    
    def get_steward_count(self, obj):
        return obj.stewards.count()
    
    def get_distance(self, obj):
        return getattr(obj, 'distance', None)
