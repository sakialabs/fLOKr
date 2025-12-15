from rest_framework import serializers
from django.utils import timezone
from .models import Reservation
from inventory.serializers import InventoryItemListSerializer
from users.serializers import UserProfileSerializer
from hubs.serializers import HubListSerializer


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model."""
    user_details = UserProfileSerializer(source='user', read_only=True)
    item_details = InventoryItemListSerializer(source='item', read_only=True)
    hub_details = HubListSerializer(source='hub', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'user_details', 'item', 'item_details', 'hub', 'hub_details',
            'quantity', 'status', 'reservation_date', 'pickup_date', 'expected_return_date',
            'actual_return_date', 'extension_requested', 'extension_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reservation_date', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate reservation data."""
        item = data.get('item')
        quantity = data.get('quantity', 1)
        pickup_date = data.get('pickup_date')
        expected_return_date = data.get('expected_return_date')
        
        # Check item availability
        if item and quantity > item.quantity_available:
            raise serializers.ValidationError({
                'quantity': f'Only {item.quantity_available} items available'
            })
        
        # Check dates
        if pickup_date and pickup_date < timezone.now().date():
            raise serializers.ValidationError({
                'pickup_date': 'Pickup date cannot be in the past'
            })
        
        if expected_return_date and pickup_date and expected_return_date <= pickup_date:
            raise serializers.ValidationError({
                'expected_return_date': 'Return date must be after pickup date'
            })
        
        return data
    
    def create(self, validated_data):
        """Create reservation and update item availability."""
        item = validated_data['item']
        quantity = validated_data['quantity']
        
        # Create reservation
        reservation = Reservation.objects.create(**validated_data)
        
        # Update item availability
        item.quantity_available -= quantity
        item.save()
        
        return reservation


class ReservationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for reservation lists."""
    item_name = serializers.CharField(source='item.name', read_only=True)
    hub_name = serializers.CharField(source='hub.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'item_name', 'hub_name', 'user_name', 'quantity',
            'status', 'pickup_date', 'expected_return_date', 'created_at'
        ]
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reservations."""
    
    class Meta:
        model = Reservation
        fields = [
            'item', 'hub', 'quantity', 'pickup_date', 'expected_return_date'
        ]
    
    def validate(self, data):
        """Validate reservation data."""
        item = data.get('item')
        quantity = data.get('quantity', 1)
        
        # Check if user has borrowing restrictions
        user = self.context['request'].user
        if user.borrowing_restricted_until and user.borrowing_restricted_until > timezone.now():
            raise serializers.ValidationError(
                f'Your borrowing privileges are restricted until {user.borrowing_restricted_until}'
            )
        
        # Check item availability
        if quantity > item.quantity_available:
            raise serializers.ValidationError({
                'quantity': f'Only {item.quantity_available} items available'
            })
        
        # Validate dates
        pickup_date = data.get('pickup_date')
        expected_return_date = data.get('expected_return_date')
        
        if pickup_date < timezone.now().date():
            raise serializers.ValidationError({
                'pickup_date': 'Pickup date cannot be in the past'
            })
        
        if expected_return_date <= pickup_date:
            raise serializers.ValidationError({
                'expected_return_date': 'Return date must be after pickup date'
            })
        
        return data
    
    def create(self, validated_data):
        # Set user to current user
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'confirmed'
        
        # Create reservation
        item = validated_data['item']
        quantity = validated_data['quantity']
        
        reservation = Reservation.objects.create(**validated_data)
        
        # Update item availability
        item.quantity_available -= quantity
        item.save()
        
        return reservation
