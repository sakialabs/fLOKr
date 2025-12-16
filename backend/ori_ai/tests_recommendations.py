"""
Tests for Ori AI Recommendation Engine

**Feature: flokr-platform, Property 17: Personalized recommendations generation**
**Feature: flokr-platform, Property 18: Complementary item suggestions**
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import from_model

from ori_ai.recommender import ItemRecommender
from inventory.models import InventoryItem
from hubs.models import Hub
from reservations.models import Reservation

User = get_user_model()


@pytest.fixture
def recommender():
    """Get recommender instance."""
    return ItemRecommender()


@pytest.fixture
def hub(db):
    """Create a test hub."""
    from django.contrib.gis.geos import Point
    return Hub.objects.create(
        name="Test Hub",
        address="123 Test St",
        location=Point(-79.3832, 43.6532),  # Toronto coordinates
        operating_hours={"mon-fri": "9-5"}
    )


@pytest.fixture
def newcomer_user(db, hub):
    """Create a newcomer user."""
    return User.objects.create_user(
        email="newcomer@test.com",
        password="test123",
        first_name="New",
        last_name="Comer",
        role="newcomer",
        assigned_hub=hub
    )


@pytest.fixture
def regular_user(db, hub):
    """Create a regular user (not newcomer)."""
    user = User.objects.create_user(
        email="regular@test.com",
        password="test123",
        first_name="Regular",
        last_name="User",
        role="community_member",
        assigned_hub=hub
    )
    # Make them "old" (> 90 days)
    user.date_joined = timezone.now() - timedelta(days=100)
    user.save()
    return user


@pytest.fixture
def winter_item(db, hub):
    """Create a winter item."""
    return InventoryItem.objects.create(
        hub=hub,
        name="Winter Coat",
        description="Warm winter coat",
        category="clothing",
        tags=["winter_coat", "warm_clothing"],
        condition="good",
        quantity_total=5,
        quantity_available=5,
        status="available"
    )


@pytest.fixture
def kitchen_items(db, hub):
    """Create complementary kitchen items."""
    items = []
    for name, tag in [
        ("Pots and Pans", "pots_pans"),
        ("Utensils", "utensils"),
        ("Dishes", "dishes"),
    ]:
        item = InventoryItem.objects.create(
            hub=hub,
            name=name,
            description=f"Kitchen {name}",
            category="kitchen",
            tags=[tag, "kitchen"],
            condition="good",
            quantity_total=3,
            quantity_available=3,
            status="available"
        )
        items.append(item)
    return items


# ============================================================================
# Property 17: Personalized recommendations generation
# ============================================================================

@pytest.mark.django_db
class TestPersonalizedRecommendations:
    """
    **Property 17: Personalized recommendations generation**
    *For any* user with completed preference data, the recommendation engine 
    should generate item suggestions based on their preferences, season, and 
    historical patterns.
    **Validates: Requirements 5.1, 5.3**
    """
    
    def test_recommendations_generated_for_any_user(
        self, recommender, newcomer_user, winter_item
    ):
        """Recommendations should be generated for any user."""
        recommendations = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=10
        )
        
        # Should return a list (may be empty if no items match)
        assert isinstance(recommendations, list)
    
    def test_recommendations_include_seasonal_items(
        self, recommender, newcomer_user, winter_item
    ):
        """Recommendations should consider current season."""
        # Mock winter season
        import ori_ai.recommender as rec_module
        original_season = rec_module.ItemRecommender._get_current_season
        rec_module.ItemRecommender._get_current_season = lambda self: 'winter'
        
        try:
            recommendations = recommender.get_personalized_recommendations(
                user=newcomer_user,
                limit=10
            )
            
            # Winter items should be recommended in winter
            recommended_items = [r['item'] for r in recommendations]
            assert winter_item in recommended_items
        finally:
            rec_module.ItemRecommender._get_current_season = original_season
    
    def test_recommendations_prioritize_newcomer_essentials(
        self, recommender, newcomer_user, regular_user, hub
    ):
        """Newcomers should get essential items prioritized."""
        # Create essential item
        essential = InventoryItem.objects.create(
            hub=hub,
            name="Bed Frame",
            description="Essential bed frame",
            category="furniture",
            tags=["bed_frame"],
            condition="good",
            quantity_total=2,
            quantity_available=2,
            status="available"
        )
        
        # Get recommendations for newcomer
        newcomer_recs = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=10
        )
        
        # Get recommendations for regular user
        regular_recs = recommender.get_personalized_recommendations(
            user=regular_user,
            limit=10
        )
        
        # Find scores for essential item
        newcomer_score = next(
            (r['score'] for r in newcomer_recs if r['item'] == essential),
            0
        )
        regular_score = next(
            (r['score'] for r in regular_recs if r['item'] == essential),
            0
        )
        
        # Newcomer should get higher score for essentials
        assert newcomer_score > regular_score
    
    def test_recommendations_exclude_reserved_items(
        self, recommender, newcomer_user, winter_item
    ):
        """Items already reserved by user should be excluded."""
        # Create reservation
        Reservation.objects.create(
            user=newcomer_user,
            item=winter_item,
            hub=winter_item.hub,
            quantity=1,
            status="confirmed",
            pickup_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7)
        )
        
        # Get recommendations
        recommendations = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=10,
            exclude_reserved=True
        )
        
        # Reserved item should not be in recommendations
        recommended_items = [r['item'] for r in recommendations]
        assert winter_item not in recommended_items
    
    def test_recommendations_sorted_by_score(
        self, recommender, newcomer_user, hub
    ):
        """Recommendations should be sorted by score (highest first)."""
        # Create items with different relevance
        items = []
        for i in range(5):
            item = InventoryItem.objects.create(
                hub=hub,
                name=f"Item {i}",
                description=f"Test item {i}",
                category="misc",
                tags=[],
                condition="good",
                quantity_total=1,
                quantity_available=1,
                status="available"
            )
            items.append(item)
        
        recommendations = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=10
        )
        
        # Verify scores are in descending order
        scores = [r['score'] for r in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    def test_recommendations_respect_limit(
        self, recommender, newcomer_user, hub
    ):
        """Recommendations should respect the limit parameter."""
        # Create many items
        for i in range(20):
            InventoryItem.objects.create(
                hub=hub,
                name=f"Item {i}",
                description=f"Test item {i}",
                category="misc",
                tags=[],
                condition="good",
                quantity_total=1,
                quantity_available=1,
                status="available"
            )
        
        # Request limited recommendations
        recommendations = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=5
        )
        
        # Should return at most 5
        assert len(recommendations) <= 5
    
    def test_recommendations_only_available_items(
        self, recommender, newcomer_user, hub
    ):
        """Only available items should be recommended."""
        # Create unavailable item
        unavailable = InventoryItem.objects.create(
            hub=hub,
            name="Unavailable Item",
            description="Not available",
            category="misc",
            tags=[],
            condition="good",
            quantity_total=1,
            quantity_available=0,  # Not available
            status="available"
        )
        
        recommendations = recommender.get_personalized_recommendations(
            user=newcomer_user,
            limit=10
        )
        
        # Unavailable item should not be recommended
        recommended_items = [r['item'] for r in recommendations]
        assert unavailable not in recommended_items


# ============================================================================
# Property 18: Complementary item suggestions
# ============================================================================

@pytest.mark.django_db
class TestComplementaryItems:
    """
    **Property 18: Complementary item suggestions**
    *For any* item being viewed, the recommendation engine should suggest 
    items that are frequently borrowed together with the viewed item.
    **Validates: Requirements 5.4**
    """
    
    def test_complementary_items_returned_for_any_item(
        self, recommender, kitchen_items
    ):
        """Complementary items should be returned for any item."""
        item = kitchen_items[0]
        
        complementary = recommender.get_complementary_items(
            item=item,
            limit=5
        )
        
        # Should return a list
        assert isinstance(complementary, list)
    
    def test_complementary_items_same_category(
        self, recommender, kitchen_items
    ):
        """Complementary items should be from same category."""
        pots = kitchen_items[0]  # Pots and Pans
        
        complementary = recommender.get_complementary_items(
            item=pots,
            limit=5
        )
        
        # Should suggest other kitchen items
        comp_items = [c['item'] for c in complementary]
        
        # Should include utensils and dishes (other kitchen items)
        assert len(comp_items) > 0
        for comp_item in comp_items:
            assert 'kitchen' in (comp_item.tags or [])
    
    def test_complementary_items_exclude_original(
        self, recommender, kitchen_items
    ):
        """Original item should not be in complementary suggestions."""
        item = kitchen_items[0]
        
        complementary = recommender.get_complementary_items(
            item=item,
            limit=5
        )
        
        # Original item should not be suggested
        comp_items = [c['item'] for c in complementary]
        assert item not in comp_items
    
    def test_complementary_items_respect_limit(
        self, recommender, hub
    ):
        """Complementary items should respect limit parameter."""
        # Create many kitchen items
        base_item = InventoryItem.objects.create(
            hub=hub,
            name="Base Kitchen Item",
            description="Base",
            category="kitchen",
            tags=["pots_pans", "kitchen"],
            condition="good",
            quantity_total=1,
            quantity_available=1,
            status="available"
        )
        
        # Create 10 complementary items
        for i in range(10):
            InventoryItem.objects.create(
                hub=hub,
                name=f"Kitchen Item {i}",
                description=f"Item {i}",
                category="kitchen",
                tags=["utensils", "kitchen"],
                condition="good",
                quantity_total=1,
                quantity_available=1,
                status="available"
            )
        
        # Request limited complementary items
        complementary = recommender.get_complementary_items(
            item=base_item,
            limit=3
        )
        
        # Should return at most 3
        assert len(complementary) <= 3
    
    def test_complementary_items_only_available(
        self, recommender, hub
    ):
        """Only available items should be suggested as complementary."""
        base_item = InventoryItem.objects.create(
            hub=hub,
            name="Base Item",
            description="Base",
            category="kitchen",
            tags=["pots_pans", "kitchen"],
            condition="good",
            quantity_total=1,
            quantity_available=1,
            status="available"
        )
        
        # Create unavailable complementary item
        unavailable = InventoryItem.objects.create(
            hub=hub,
            name="Unavailable Kitchen Item",
            description="Not available",
            category="kitchen",
            tags=["utensils", "kitchen"],
            condition="good",
            quantity_total=1,
            quantity_available=0,  # Not available
            status="available"
        )
        
        complementary = recommender.get_complementary_items(
            item=base_item,
            limit=10
        )
        
        # Unavailable item should not be suggested
        comp_items = [c['item'] for c in complementary]
        assert unavailable not in comp_items
    
    def test_complementary_items_empty_for_unmatched_category(
        self, recommender, hub
    ):
        """Items without matching category should return empty list."""
        # Create item with no complementary category
        item = InventoryItem.objects.create(
            hub=hub,
            name="Random Item",
            description="No category match",
            category="misc",
            tags=["random", "unique"],
            condition="good",
            quantity_total=1,
            quantity_available=1,
            status="available"
        )
        
        complementary = recommender.get_complementary_items(
            item=item,
            limit=5
        )
        
        # Should return empty list (no matching category)
        assert len(complementary) == 0


# ============================================================================
# Additional Recommendation Tests
# ============================================================================

@pytest.mark.django_db
class TestSeasonalRecommendations:
    """Test seasonal recommendation logic."""
    
    def test_seasonal_recommendations_match_season(
        self, recommender, newcomer_user, winter_item
    ):
        """Seasonal recommendations should match current season."""
        # Mock winter season
        import ori_ai.recommender as rec_module
        original_season = rec_module.ItemRecommender._get_current_season
        rec_module.ItemRecommender._get_current_season = lambda self: 'winter'
        
        try:
            recommendations = recommender.get_seasonal_recommendations(
                user=newcomer_user,
                limit=5
            )
            
            # Should include winter items
            if len(recommendations) > 0:
                for rec in recommendations:
                    assert rec['season'] == 'winter'
        finally:
            rec_module.ItemRecommender._get_current_season = original_season


@pytest.mark.django_db
class TestNewcomerEssentials:
    """Test newcomer essentials logic."""
    
    def test_newcomer_essentials_only_for_newcomers(
        self, recommender, newcomer_user, regular_user, hub
    ):
        """Essentials should only be returned for newcomers."""
        # Create essential item
        InventoryItem.objects.create(
            hub=hub,
            name="Bed Frame",
            description="Essential",
            category="furniture",
            tags=["bed_frame"],
            condition="good",
            quantity_total=1,
            quantity_available=1,
            status="available"
        )
        
        # Newcomer should get essentials
        newcomer_essentials = recommender.get_newcomer_essentials(
            user=newcomer_user,
            limit=10
        )
        assert len(newcomer_essentials) > 0
        
        # Regular user should get empty list
        regular_essentials = recommender.get_newcomer_essentials(
            user=regular_user,
            limit=10
        )
        assert len(regular_essentials) == 0