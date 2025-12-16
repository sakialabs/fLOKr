"""
Ori AI API Views
Provides endpoints for image tagging and other AI services
"""
import time
import logging
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers import (
    ImageTagRequestSerializer, 
    ImageTagResponseSerializer,
    RecommendationSerializer,
    QuestionRequestSerializer,
    QuestionResponseSerializer,
    FAQEntrySerializer
)
from .image_tagger import get_image_tagger
from .recommender import recommender

logger = logging.getLogger(__name__)


class ImageTagView(APIView):
    """
    Generate tags and category suggestions for item images
    Uses pre-trained ResNet50 model for automatic tagging
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ImageTagRequestSerializer,
        responses={200: ImageTagResponseSerializer},
        description="Generate tags and category for an image",
        tags=['Ori AI']
    )
    def post(self, request):
        """
        Generate tags for an uploaded image or image URL
        
        Returns suggested tags and category within 5 seconds
        """
        start_time = time.time()
        
        # Validate request
        serializer = ImageTagRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get image data
            image_data = None
            
            if 'image_file' in request.FILES:
                # Read uploaded file
                image_file = request.FILES['image_file']
                image_data = image_file.read()
                logger.info(f"Processing uploaded image: {image_file.name}")
                
            elif serializer.validated_data.get('image_url'):
                # Download image from URL
                image_url = serializer.validated_data['image_url']
                logger.info(f"Downloading image from URL: {image_url}")
                
                response = requests.get(image_url, timeout=5)
                response.raise_for_status()
                image_data = response.content
            
            if not image_data:
                return Response(
                    {"error": "No image data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get image tagger
            tagger = get_image_tagger()
            
            # Generate tags and category
            tags, category = tagger.suggest_tags_and_category(image_data)
            
            # Get detailed tags with confidence
            detailed_tags = tagger.generate_tags(image_data, top_k=5)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare response
            response_data = {
                'tags': tags,
                'category': category,
                'detailed_tags': detailed_tags,
                'processing_time': round(processing_time, 2)
            }
            
            logger.info(
                f"Image tagging completed in {processing_time:.2f}s: "
                f"{len(tags)} tags, category: {category}"
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            return Response(
                {"error": f"Failed to download image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            logger.error(f"Invalid image data: {e}")
            return Response(
                {"error": f"Invalid image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Image tagging failed: {e}")
            return Response(
                {"error": "Image tagging service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class RecommendationsView(APIView):
    """
    Get personalized item recommendations
    Uses collaborative filtering and user preferences
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of recommendations (default: 10)',
                required=False
            ),
        ],
        responses={200: RecommendationSerializer(many=True)},
        description="Get personalized item recommendations based on user preferences, season, and community patterns",
        tags=['Ori AI']
    )
    def get(self, request):
        """
        Get personalized recommendations for the authenticated user
        
        Factors considered:
        - User preferences and history
        - Current season
        - Newcomer status
        - Hub proximity
        - Community patterns
        """
        limit = int(request.query_params.get('limit', 10))
        
        try:
            recommendations = recommender.get_personalized_recommendations(
                user=request.user,
                limit=limit
            )
            
            # Serialize response
            serializer = RecommendationSerializer(recommendations, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return Response(
                {"error": "Recommendation service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SeasonalRecommendationsView(APIView):
    """
    Get seasonal item recommendations
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of recommendations (default: 5)',
                required=False
            ),
        ],
        responses={200: RecommendationSerializer(many=True)},
        description="Get seasonal item recommendations appropriate for current time of year",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get seasonal recommendations"""
        limit = int(request.query_params.get('limit', 5))
        
        try:
            recommendations = recommender.get_seasonal_recommendations(
                user=request.user,
                limit=limit
            )
            
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Seasonal recommendations failed: {e}")
            return Response(
                {"error": "Recommendation service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ComplementaryItemsView(APIView):
    """
    Get items that complement a specific item
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=int,
                description='ID of the item to find complements for',
                required=True
            ),
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of recommendations (default: 5)',
                required=False
            ),
        ],
        responses={200: RecommendationSerializer(many=True)},
        description="Get items frequently borrowed together with the specified item",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get complementary items"""
        from inventory.models import InventoryItem
        
        item_id = request.query_params.get('item_id')
        limit = int(request.query_params.get('limit', 5))
        
        if not item_id:
            return Response(
                {"error": "item_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            recommendations = recommender.get_complementary_items(
                item=item,
                limit=limit
            )
            
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Complementary items failed: {e}")
            return Response(
                {"error": "Recommendation service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NewcomerEssentialsView(APIView):
    """
    Get essential items for newcomers
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of recommendations (default: 10)',
                required=False
            ),
        ],
        responses={200: RecommendationSerializer(many=True)},
        description="Get essential items recommended for newcomers",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get newcomer essentials"""
        limit = int(request.query_params.get('limit', 10))
        
        try:
            recommendations = recommender.get_newcomer_essentials(
                user=request.user,
                limit=limit
            )
            
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Newcomer essentials failed: {e}")
            return Response(
                {"error": "Recommendation service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PopularItemsView(APIView):
    """
    Get most popular items in the community
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='hub_id',
                type=int,
                description='Filter by hub ID (optional)',
                required=False
            ),
            OpenApiParameter(
                name='days',
                type=int,
                description='Number of days to look back (default: 30)',
                required=False
            ),
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of items (default: 10)',
                required=False
            ),
        ],
        responses={200: RecommendationSerializer(many=True)},
        description="Get most popular items based on recent reservation history",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get popular items"""
        from hubs.models import Hub
        
        hub_id = request.query_params.get('hub_id')
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))
        
        hub = None
        if hub_id:
            try:
                hub = Hub.objects.get(id=hub_id)
            except Hub.DoesNotExist:
                return Response(
                    {"error": "Hub not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            recommendations = recommender.get_popular_items(
                hub=hub,
                days=days,
                limit=limit
            )
            
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Popular items failed: {e}")
            return Response(
                {"error": "Recommendation service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class AskQuestionView(APIView):
    """
    Natural language Q&A endpoint
    Answers questions using FAQ knowledge base and semantic search
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=QuestionRequestSerializer,
        responses={200: QuestionResponseSerializer},
        description="Ask a natural language question and get an answer from the FAQ knowledge base",
        tags=['Ori AI'],
        examples=[
            OpenApiExample(
                'How to borrow items',
                value={
                    'question': 'How do I borrow an item from the hub?',
                    'category': 'borrowing',
                    'limit': 3
                }
            ),
            OpenApiExample(
                'General question',
                value={
                    'question': 'What is a hub?',
                    'limit': 5
                }
            ),
        ]
    )
    def post(self, request):
        """
        Answer a natural language question
        
        Uses semantic search to find relevant FAQ entries.
        Returns answer within 10 seconds with confidence score.
        """
        from .serializers import QuestionRequestSerializer, QuestionResponseSerializer
        from .qa_service import qa_service
        
        # Validate request
        serializer = QuestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question = serializer.validated_data['question']
        category = serializer.validated_data.get('category')
        limit = serializer.validated_data.get('limit', 3)
        
        try:
            # Get answer from Q&A service
            result = qa_service.ask(
                question=question,
                category=category,
                limit=limit
            )
            
            # Validate response time (should be < 10 seconds)
            if result['response_time'] > 10:
                logger.warning(
                    f"Q&A response time exceeded 10s: {result['response_time']:.2f}s"
                )
            
            logger.info(
                f"Q&A answered in {result['response_time']:.2f}s "
                f"(confidence: {result['confidence']:.2f}, method: {result['method']})"
            )
            
            # Serialize and return
            response_serializer = QuestionResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Q&A service failed: {e}")
            return Response(
                {"error": "Q&A service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PopularFAQsView(APIView):
    """
    Get most popular/helpful FAQ entries
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of FAQs (default: 10)',
                required=False
            ),
        ],
        responses={200: FAQEntrySerializer(many=True)},
        description="Get most popular and helpful FAQ entries",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get popular FAQs"""
        from .serializers import FAQEntrySerializer
        from .qa_service import qa_service
        
        limit = int(request.query_params.get('limit', 10))
        
        try:
            faqs = qa_service.get_popular_faqs(limit=limit)
            return Response(faqs, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Popular FAQs failed: {e}")
            return Response(
                {"error": "FAQ service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FAQsByCategoryView(APIView):
    """
    Get FAQs filtered by category
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                type=str,
                description='Category to filter by',
                required=True
            ),
            OpenApiParameter(
                name='limit',
                type=int,
                description='Maximum number of FAQs (default: 10)',
                required=False
            ),
        ],
        responses={200: FAQEntrySerializer(many=True)},
        description="Get FAQ entries filtered by category",
        tags=['Ori AI']
    )
    def get(self, request):
        """Get FAQs by category"""
        from .serializers import FAQEntrySerializer
        from .qa_service import qa_service
        
        category = request.query_params.get('category')
        limit = int(request.query_params.get('limit', 10))
        
        if not category:
            return Response(
                {"error": "category parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            faqs = qa_service.get_faqs_by_category(
                category=category,
                limit=limit
            )
            return Response(faqs, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"FAQs by category failed: {e}")
            return Response(
                {"error": "FAQ service temporarily unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
