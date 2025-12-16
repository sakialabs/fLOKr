from rest_framework import serializers


class ImageTagRequestSerializer(serializers.Serializer):
    """Serializer for image tag generation request"""
    image_url = serializers.URLField(
        required=False,
        help_text="URL of the image to tag"
    )
    image_file = serializers.ImageField(
        required=False,
        help_text="Image file to tag"
    )
    
    def validate(self, data):
        """Ensure either image_url or image_file is provided"""
        if not data.get('image_url') and not data.get('image_file'):
            raise serializers.ValidationError(
                "Either image_url or image_file must be provided"
            )
        return data


class TagSerializer(serializers.Serializer):
    """Serializer for individual tag"""
    tag = serializers.CharField()
    confidence = serializers.FloatField()


class ImageTagResponseSerializer(serializers.Serializer):
    """Serializer for image tag generation response"""
    tags = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of suggested tags"
    )
    category = serializers.CharField(
        help_text="Suggested category for the item"
    )
    detailed_tags = TagSerializer(
        many=True,
        help_text="Detailed tags with confidence scores"
    )
    processing_time = serializers.FloatField(
        help_text="Processing time in seconds"
    )



class RecommendationSerializer(serializers.Serializer):
    """Serializer for item recommendations"""
    item = serializers.SerializerMethodField()
    score = serializers.FloatField(required=False)
    reason = serializers.CharField(required=False)
    reasons = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    season = serializers.CharField(required=False)
    reservation_count = serializers.IntegerField(required=False)
    
    def get_item(self, obj):
        """Serialize the item data"""
        from inventory.serializers import InventoryItemSerializer
        item = obj.get('item')
        if item:
            return InventoryItemSerializer(item).data
        return None


class FAQEntrySerializer(serializers.Serializer):
    """Serializer for FAQ entries"""
    id = serializers.UUIDField(read_only=True)
    question = serializers.CharField()
    answer = serializers.CharField()
    category = serializers.CharField()
    keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    view_count = serializers.IntegerField(read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)


class QuestionRequestSerializer(serializers.Serializer):
    """Serializer for Q&A request"""
    question = serializers.CharField(
        required=True,
        help_text="The natural language question to ask"
    )
    category = serializers.CharField(
        required=False,
        help_text="Optional category filter"
    )
    limit = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=10,
        help_text="Maximum number of related FAQs to return"
    )


class RelatedFAQSerializer(serializers.Serializer):
    """Serializer for related FAQ"""
    question = serializers.CharField()
    answer = serializers.CharField()
    category = serializers.CharField()
    score = serializers.FloatField()


class QuestionResponseSerializer(serializers.Serializer):
    """Serializer for Q&A response"""
    answer = serializers.CharField(
        help_text="The answer to the question"
    )
    confidence = serializers.FloatField(
        help_text="Confidence score (0.0 to 1.0)"
    )
    question_matched = serializers.CharField(
        allow_null=True,
        help_text="The FAQ question that was matched"
    )
    category = serializers.CharField(
        allow_null=True,
        help_text="Category of the matched FAQ"
    )
    related_faqs = RelatedFAQSerializer(
        many=True,
        help_text="Related FAQ entries"
    )
    response_time = serializers.FloatField(
        help_text="Response time in seconds"
    )
    method = serializers.CharField(
        help_text="Search method used (semantic/keyword/fallback)"
    )
