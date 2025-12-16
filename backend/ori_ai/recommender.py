"""
Ori AI - Recommendation Engine

Provides personalized item recommendations using:
- User preferences and history
- Seasonal patterns
- Collaborative filtering
- Complementary item suggestions
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter, defaultdict
from django.db.models import Count, Q, F
from django.utils import timezone


class ItemRecommender:
    """
    Recommendation engine for inventory items.
    Uses collaborative filtering and content-based filtering.
    """
    
    # Seasonal item categories
    SEASONAL_ITEMS = {
        'winter': ['winter_coat', 'boots', 'heater', 'blanket', 'warm_clothing'],
        'spring': ['rain_jacket', 'umbrella', 'gardening_tools', 'bicycle'],
        'summer': ['fan', 'cooler', 'camping_gear', 'sports_equipment'],
        'fall': ['jacket', 'rain_gear', 'school_supplies', 'backpack']
    }
    
    # Complementary item pairs (items frequently borrowed together)
    COMPLEMENTARY_ITEMS = {
        'kitchen': ['pots_pans', 'utensils', 'dishes', 'cutting_board', 'knife_set'],
        'bedroom': ['bed_frame', 'mattress', 'bedding', 'pillow', 'lamp'],
        'cleaning': ['vacuum', 'mop', 'broom', 'cleaning_supplies', 'bucket'],
        'office': ['desk', 'chair', 'lamp', 'organizer', 'supplies'],
        'baby': ['crib', 'stroller', 'car_seat', 'high_chair', 'baby_monitor'],
        'winter': ['winter_coat', 'boots', 'gloves', 'hat', 'scarf'],
    }
    
    # Essential items for newcomers
    NEWCOMER_ESSENTIALS = [
        'bed_frame', 'mattress', 'bedding', 'pillow',
        'pots_pans', 'dishes', 'utensils',
        'cleaning_supplies', 'vacuum',
        'winter_coat', 'boots',  # Seasonal
    ]
    
    def __init__(self):
        """Initialize the recommender."""
        pass
    
    def get_personalized_recommendations(
        self, 
        user, 
        limit: int = 10,
        exclude_reserved: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user.
        
        Args:
            user: User instance
            limit: Maximum number of recommendations
            exclude_reserved: Exclude items user has already reserved
            
        Returns:
            List of recommended items with scores
        """
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        
        recommendations = []
        
        # Get available items
        items = InventoryItem.objects.filter(
            status='available',
            quantity_available__gt=0
        )
        
        # Exclude items user has already reserved
        if exclude_reserved:
            reserved_item_ids = Reservation.objects.filter(
                user=user,
                status__in=['pending', 'confirmed', 'picked_up']
            ).values_list('item_id', flat=True)
            items = items.exclude(id__in=reserved_item_ids)
        
        # Score each item
        for item in items:
            score = self._calculate_item_score(user, item)
            if score > 0:
                recommendations.append({
                    'item': item,
                    'score': score,
                    'reasons': self._get_recommendation_reasons(user, item)
                })
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def get_seasonal_recommendations(
        self,
        user,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get seasonal item recommendations.
        
        Args:
            user: User instance
            limit: Maximum number of recommendations
            
        Returns:
            List of seasonal items
        """
        from inventory.models import InventoryItem
        
        season = self._get_current_season()
        seasonal_tags = self.SEASONAL_ITEMS.get(season, [])
        
        # Find items with seasonal tags
        items = InventoryItem.objects.filter(
            status='available',
            quantity_available__gt=0
        )
        
        seasonal_items = []
        for item in items:
            # Check if item has seasonal tags
            item_tags = item.tags or []
            if any(tag in seasonal_tags for tag in item_tags):
                seasonal_items.append({
                    'item': item,
                    'season': season,
                    'reason': f'Recommended for {season}'
                })
        
        return seasonal_items[:limit]
    
    def get_complementary_items(
        self,
        item,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get items that complement the given item.
        
        Args:
            item: InventoryItem instance
            limit: Maximum number of recommendations
            
        Returns:
            List of complementary items
        """
        from inventory.models import InventoryItem
        
        complementary = []
        item_tags = item.tags or []
        
        # Find complementary category
        comp_category = None
        for category, tags in self.COMPLEMENTARY_ITEMS.items():
            if any(tag in item_tags for tag in tags):
                comp_category = category
                break
        
        if not comp_category:
            return []
        
        # Get other items in the same complementary category
        comp_tags = self.COMPLEMENTARY_ITEMS[comp_category]
        
        items = InventoryItem.objects.filter(
            status='available',
            quantity_available__gt=0
        ).exclude(id=item.id)
        
        for candidate in items:
            candidate_tags = candidate.tags or []
            if any(tag in comp_tags for tag in candidate_tags):
                complementary.append({
                    'item': candidate,
                    'reason': f'Often borrowed with {item.name}'
                })
        
        return complementary[:limit]
    
    def get_newcomer_essentials(
        self,
        user,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get essential items for newcomers.
        
        Args:
            user: User instance
            limit: Maximum number of recommendations
            
        Returns:
            List of essential items
        """
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        
        # Check if user is a newcomer (registered within last 3 months)
        is_newcomer = (
            user.role == 'newcomer' or
            (timezone.now() - user.date_joined).days <= 90
        )
        
        if not is_newcomer:
            return []
        
        # Get items user hasn't reserved yet
        reserved_item_ids = Reservation.objects.filter(
            user=user
        ).values_list('item_id', flat=True)
        
        # Find essential items
        items = InventoryItem.objects.filter(
            status='available',
            quantity_available__gt=0
        ).exclude(id__in=reserved_item_ids)
        
        essentials = []
        for item in items:
            item_tags = item.tags or []
            if any(tag in self.NEWCOMER_ESSENTIALS for tag in item_tags):
                essentials.append({
                    'item': item,
                    'reason': 'Essential for newcomers'
                })
        
        # Add seasonal essentials
        season = self._get_current_season()
        if season == 'winter':
            # Prioritize winter items
            essentials.sort(
                key=lambda x: any(
                    tag in ['winter_coat', 'boots', 'heater', 'blanket']
                    for tag in (x['item'].tags or [])
                ),
                reverse=True
            )
        
        return essentials[:limit]
    
    def get_popular_items(
        self,
        hub=None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular items based on reservation history.
        
        Args:
            hub: Optional hub to filter by
            days: Number of days to look back
            limit: Maximum number of items
            
        Returns:
            List of popular items
        """
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        
        since = timezone.now() - timedelta(days=days)
        
        # Get reservation counts
        reservations = Reservation.objects.filter(
            created_at__gte=since
        )
        
        if hub:
            reservations = reservations.filter(item__hub=hub)
        
        # Count reservations per item
        popular_items = reservations.values('item').annotate(
            reservation_count=Count('id')
        ).order_by('-reservation_count')[:limit]
        
        results = []
        for data in popular_items:
            try:
                item = InventoryItem.objects.get(
                    id=data['item'],
                    status='available',
                    quantity_available__gt=0
                )
                results.append({
                    'item': item,
                    'reservation_count': data['reservation_count'],
                    'reason': f'Popular in your community ({data["reservation_count"]} reservations)'
                })
            except InventoryItem.DoesNotExist:
                continue
        
        return results
    
    def _calculate_item_score(self, user, item) -> float:
        """
        Calculate recommendation score for an item.
        
        Factors:
        - User preferences match
        - Seasonal relevance
        - Newcomer status
        - Item popularity
        - Hub proximity
        """
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Seasonal boost
        season = self._get_current_season()
        seasonal_tags = self.SEASONAL_ITEMS.get(season, [])
        item_tags = item.tags or []
        if any(tag in seasonal_tags for tag in item_tags):
            score += 2.0
        
        # Newcomer essentials boost
        is_newcomer = (
            user.role == 'newcomer' or
            (timezone.now() - user.date_joined).days <= 90
        )
        if is_newcomer and any(tag in self.NEWCOMER_ESSENTIALS for tag in item_tags):
            score += 3.0
        
        # Hub proximity boost (if user has assigned hub)
        if hasattr(user, 'assigned_hub') and user.assigned_hub == item.hub:
            score += 1.5
        
        # Category preference (if user has preferences)
        if hasattr(user, 'preferences') and user.preferences:
            prefs = user.preferences
            if item.category in (prefs.get('preferred_categories') or []):
                score += 2.0
        
        return score
    
    def _get_recommendation_reasons(self, user, item) -> List[str]:
        """Get human-readable reasons for recommendation."""
        reasons = []
        
        # Seasonal
        season = self._get_current_season()
        seasonal_tags = self.SEASONAL_ITEMS.get(season, [])
        item_tags = item.tags or []
        if any(tag in seasonal_tags for tag in item_tags):
            reasons.append(f'Perfect for {season}')
        
        # Newcomer
        is_newcomer = (
            user.role == 'newcomer' or
            (timezone.now() - user.date_joined).days <= 90
        )
        if is_newcomer and any(tag in self.NEWCOMER_ESSENTIALS for tag in item_tags):
            reasons.append('Essential for newcomers')
        
        # Hub proximity
        if hasattr(user, 'assigned_hub') and user.assigned_hub == item.hub:
            reasons.append('Available at your hub')
        
        return reasons
    
    def _get_current_season(self) -> str:
        """Determine current season based on month."""
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:  # 9, 10, 11
            return 'fall'


# Global instance
recommender = ItemRecommender()
