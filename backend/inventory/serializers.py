import logging
import requests
from rest_framework import serializers
from .models import InventoryItem, InventoryTransfer
from hubs.serializers import HubListSerializer
from users.serializers import UserProfileSerializer

logger = logging.getLogger(__name__)


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model."""
    hub_details = HubListSerializer(source='hub', read_only=True)
    donor_details = UserProfileSerializer(source='donor', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'hub', 'hub_details', 'name', 'description', 'category',
            'tags', 'condition', 'images', 'quantity_total', 'quantity_available',
            'donor', 'donor_details', 'status', 'incident_report_count', 
            'is_flagged', 'flagged_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'incident_report_count', 
                           'is_flagged', 'flagged_at']
    
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
    """Serializer for creating inventory items with automatic image tagging."""
    auto_tag = serializers.BooleanField(
        default=True,
        write_only=True,
        help_text="Automatically generate tags and category from first image"
    )
    suggested_tags = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="AI-suggested tags based on image analysis"
    )
    suggested_category = serializers.CharField(
        read_only=True,
        help_text="AI-suggested category based on image analysis"
    )
    
    class Meta:
        model = InventoryItem
        fields = [
            'hub', 'name', 'description', 'category', 'tags', 'condition',
            'images', 'quantity_total', 'quantity_available', 'donor',
            'auto_tag', 'suggested_tags', 'suggested_category'
        ]
    
    def _get_image_tags(self, image_url):
        """
        Get tags and category from Ori AI image tagging service
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Tuple of (tags_list, category_string) or (None, None) on failure
        """
        try:
            from ori_ai.image_tagger import get_image_tagger
            
            # Download image
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            image_data = response.content
            
            # Get tagger and generate tags
            tagger = get_image_tagger()
            tags, category = tagger.suggest_tags_and_category(image_data)
            
            logger.info(f"Auto-tagged image: {len(tags)} tags, category: {category}")
            return tags, category
            
        except Exception as e:
            logger.warning(f"Auto-tagging failed: {e}")
            return None, None
    
    def create(self, validated_data):
        # Extract auto_tag flag
        auto_tag = validated_data.pop('auto_tag', True)
        
        # Set donor to current user if not provided
        if 'donor' not in validated_data:
            validated_data['donor'] = self.context['request'].user
        
        # Auto-tag if enabled and images provided
        if auto_tag and validated_data.get('images'):
            first_image = validated_data['images'][0]
            suggested_tags, suggested_category = self._get_image_tags(first_image)
            
            if suggested_tags:
                # Merge suggested tags with existing tags
                existing_tags = validated_data.get('tags', [])
                if isinstance(existing_tags, str):
                    existing_tags = [tag.strip() for tag in existing_tags.split(',')]
                
                # Combine and deduplicate tags
                all_tags = list(set(existing_tags + suggested_tags))
                validated_data['tags'] = all_tags
                
                # Store suggestions for response
                self._suggested_tags = suggested_tags
                self._suggested_category = suggested_category
                
                # Auto-set category if not provided
                if not validated_data.get('category') and suggested_category:
                    validated_data['category'] = suggested_category
                    logger.info(f"Auto-set category to: {suggested_category}")
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Include suggested tags in response"""
        data = super().to_representation(instance)
        
        # Add suggestions if available
        if hasattr(self, '_suggested_tags'):
            data['suggested_tags'] = self._suggested_tags
        if hasattr(self, '_suggested_category'):
            data['suggested_category'] = self._suggested_category
        
        return data

class InventoryTransferSerializer(serializers.ModelSerializer):
    """Serializer for InventoryTransfer model."""
    item_details = InventoryItemListSerializer(source='item', read_only=True)
    from_hub_name = serializers.CharField(source='from_hub.name', read_only=True)
    to_hub_name = serializers.CharField(source='to_hub.name', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryTransfer
        fields = [
            'id', 'item', 'item_details', 'from_hub', 'from_hub_name', 
            'to_hub', 'to_hub_name', 'quantity', 'status',
            'initiated_by', 'initiated_by_name', 'approved_by', 'approved_by_name',
            'completed_by', 'completed_by_name', 'reason', 'notes',
            'created_at', 'approved_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'approved_by', 'completed_by',
            'created_at', 'approved_at', 'completed_at', 'updated_at'
        ]