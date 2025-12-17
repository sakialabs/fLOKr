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


class TranslationRequestSerializer(serializers.Serializer):
    """Serializer for translation request"""
    text = serializers.CharField(
        required=True,
        help_text="Text to translate",
        max_length=5000
    )
    target_language = serializers.CharField(
        required=True,
        help_text="Target language code (e.g., 'es', 'ar', 'fr')",
        max_length=10
    )
    source_language = serializers.CharField(
        required=False,
        help_text="Source language code (auto-detect if not provided)",
        max_length=10
    )


class TranslationBatchRequestSerializer(serializers.Serializer):
    """Serializer for batch translation request"""
    texts = serializers.ListField(
        child=serializers.CharField(max_length=5000),
        required=True,
        help_text="List of texts to translate",
        max_length=50  # Limit to 50 texts per request
    )
    target_language = serializers.CharField(
        required=True,
        help_text="Target language code",
        max_length=10
    )
    source_language = serializers.CharField(
        required=False,
        help_text="Source language code (auto-detect if not provided)",
        max_length=10
    )


class TranslationResponseSerializer(serializers.Serializer):
    """Serializer for translation response"""
    translated_text = serializers.CharField(
        help_text="Translated text"
    )
    source_lang = serializers.CharField(
        help_text="Detected or provided source language"
    )
    target_lang = serializers.CharField(
        help_text="Target language"
    )
    cached = serializers.BooleanField(
        help_text="Whether result was served from cache"
    )
    error = serializers.CharField(
        required=False,
        help_text="Error message if translation failed"
    )


class LanguageDetectionRequestSerializer(serializers.Serializer):
    """Serializer for language detection request"""
    text = serializers.CharField(
        required=True,
        help_text="Text to analyze",
        max_length=1000
    )


class LanguageDetectionResponseSerializer(serializers.Serializer):
    """Serializer for language detection response"""
    detected_language = serializers.CharField(
        help_text="Detected language code"
    )
    language_name = serializers.CharField(
        help_text="Language name"
    )


class SupportedLanguagesSerializer(serializers.Serializer):
    """Serializer for supported languages list"""
    code = serializers.CharField(help_text="Language code")
    name = serializers.CharField(help_text="Language name")


class DemandForecastRequestSerializer(serializers.Serializer):
    """Serializer for demand forecast request"""
    item_id = serializers.IntegerField(
        required=False,
        help_text="Specific item ID to forecast"
    )
    category = serializers.CharField(
        required=False,
        help_text="Item category to forecast",
        max_length=50
    )
    hub_id = serializers.IntegerField(
        required=False,
        help_text="Hub ID to filter forecast"
    )
    days_forward = serializers.IntegerField(
        required=False,
        default=30,
        min_value=1,
        max_value=90,
        help_text="Forecast period in days (1-90)"
    )
    
    def validate(self, data):
        """Ensure at least one filter is provided"""
        if not any([data.get('item_id'), data.get('category'), data.get('hub_id')]):
            raise serializers.ValidationError(
                "At least one of item_id, category, or hub_id must be provided"
            )
        return data


class DemandForecastResponseSerializer(serializers.Serializer):
    """Serializer for demand forecast response"""
    forecast_date = serializers.DateTimeField()
    forecast_period_days = serializers.IntegerField()
    historical_data = serializers.DictField()
    newcomer_adjustment = serializers.DictField()
    seasonal_adjustment = serializers.DictField(allow_null=True)
    final_daily_forecast = serializers.FloatField()
    final_period_forecast = serializers.FloatField()
    accuracy_score = serializers.FloatField()
    confidence_level = serializers.CharField()


class HighDemandItemSerializer(serializers.Serializer):
    """Serializer for high demand item"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    category = serializers.CharField()
    current_inventory = serializers.IntegerField()
    forecasted_demand_30days = serializers.FloatField()
    demand_ratio = serializers.FloatField()
    forecast_confidence = serializers.CharField()
    recommendation = serializers.CharField()


class HighDemandAlertRequestSerializer(serializers.Serializer):
    """Serializer for high demand alert request"""
    hub_id = serializers.IntegerField(
        required=False,
        help_text="Hub ID to check"
    )
    threshold = serializers.FloatField(
        required=False,
        default=0.5,
        min_value=0.1,
        max_value=2.0,
        help_text="Demand/inventory threshold (default 0.5 = 50%)"
    )
