"""
Ori AI - Demand Forecasting Service
Predicts future demand for inventory items using time-series analysis
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.db.models import Count, Q
from django.utils import timezone
from inventory.models import InventoryItem
from reservations.models import Reservation
from users.models import User

logger = logging.getLogger(__name__)


class DemandForecaster:
    """
    Forecasts demand for inventory items based on historical data,
    seasonal patterns, and newcomer arrivals
    """
    
    # Seasonal demand multipliers by category
    SEASONAL_MULTIPLIERS = {
        'winter_clothing': {
            'winter': 2.5,  # Dec-Feb
            'spring': 0.8,  # Mar-May
            'summer': 0.3,  # Jun-Aug
            'fall': 1.2     # Sep-Nov
        },
        'summer_clothing': {
            'winter': 0.4,
            'spring': 1.3,
            'summer': 2.0,
            'fall': 0.9
        },
        'furniture': {
            'winter': 1.0,
            'spring': 1.4,  # Peak moving season
            'summer': 1.3,
            'fall': 1.2
        },
        'school_supplies': {
            'winter': 0.6,
            'spring': 0.7,
            'summer': 2.5,  # Back to school
            'fall': 1.8
        },
        'kitchenware': {
            'winter': 1.0,
            'spring': 1.2,
            'summer': 1.0,
            'fall': 1.0
        }
    }
    
    CATEGORY_MAPPING = {
        'Clothing': 'winter_clothing',  # Default to winter, will be adjusted
        'Furniture': 'furniture',
        'Kitchen': 'kitchenware',
        'Household': 'kitchenware',
        'Electronics': 'furniture',  # Stable demand
        'Books': 'school_supplies',
        'Toys': 'school_supplies',
    }
    
    def get_current_season(self) -> str:
        """Determine current season based on month"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def get_historical_demand(
        self,
        item_id: Optional[int] = None,
        category: Optional[str] = None,
        hub_id: Optional[int] = None,
        days_back: int = 90
    ) -> Dict[str, any]:
        """
        Calculate historical demand based on reservation data
        
        Args:
            item_id: Specific item ID
            category: Item category
            hub_id: Hub ID
            days_back: Number of days to look back
            
        Returns:
            Dict with demand metrics
        """
        start_date = timezone.now() - timedelta(days=days_back)
        
        # Build query
        query = Q(created_at__gte=start_date)
        
        if item_id:
            query &= Q(item_id=item_id)
        if category:
            query &= Q(item__category=category)
        if hub_id:
            query &= Q(item__hub_id=hub_id)
        
        # Get reservations
        reservations = Reservation.objects.filter(query)
        total_reservations = reservations.count()
        
        # Calculate daily average
        daily_average = total_reservations / days_back if days_back > 0 else 0
        
        # Get weekly breakdown
        weekly_demand = []
        for week in range(12):  # Last 12 weeks
            week_start = timezone.now() - timedelta(weeks=week+1)
            week_end = timezone.now() - timedelta(weeks=week)
            week_count = reservations.filter(
                created_at__gte=week_start,
                created_at__lt=week_end
            ).count()
            weekly_demand.append(week_count)
        
        # Calculate trend (simple linear)
        if len(weekly_demand) >= 2:
            recent_avg = sum(weekly_demand[:4]) / 4  # Last 4 weeks
            older_avg = sum(weekly_demand[8:]) / 4   # Weeks 9-12
            trend = 'increasing' if recent_avg > older_avg * 1.2 else \
                    'decreasing' if recent_avg < older_avg * 0.8 else 'stable'
        else:
            trend = 'stable'
        
        return {
            'total_reservations': total_reservations,
            'daily_average': round(daily_average, 2),
            'weekly_demand': weekly_demand,
            'trend': trend,
            'period_days': days_back
        }
    
    def get_newcomer_adjusted_forecast(
        self,
        base_demand: float,
        hub_id: Optional[int] = None,
        days_forward: int = 30
    ) -> Dict[str, any]:
        """
        Adjust forecast based on expected newcomer arrivals
        
        Args:
            base_demand: Base daily demand
            hub_id: Hub ID
            days_forward: Forecast period
            
        Returns:
            Dict with adjusted forecast
        """
        # Get recent newcomer arrival rate
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        query = Q(
            role='newcomer',
            date_joined__gte=thirty_days_ago
        )
        if hub_id:
            query &= Q(assigned_hub_id=hub_id)
        
        recent_newcomers = User.objects.filter(query).count()
        newcomer_rate = recent_newcomers / 30  # per day
        
        # Assume each newcomer needs ~5 essential items in first month
        newcomer_demand_boost = newcomer_rate * 5 / 30  # daily demand from newcomers
        
        # Adjusted forecast
        adjusted_daily = base_demand + newcomer_demand_boost
        projected_monthly = adjusted_daily * days_forward
        
        return {
            'base_daily_demand': round(base_demand, 2),
            'newcomer_daily_boost': round(newcomer_demand_boost, 2),
            'adjusted_daily_demand': round(adjusted_daily, 2),
            'projected_demand_30days': round(projected_monthly, 1),
            'recent_newcomer_count': recent_newcomers,
            'newcomer_arrival_rate': round(newcomer_rate, 2)
        }
    
    def apply_seasonal_adjustment(
        self,
        base_demand: float,
        category: str
    ) -> Dict[str, any]:
        """
        Apply seasonal multipliers to demand forecast
        
        Args:
            base_demand: Base demand value
            category: Item category
            
        Returns:
            Dict with seasonal adjustments
        """
        current_season = self.get_current_season()
        
        # Map category to seasonal pattern
        seasonal_key = self.CATEGORY_MAPPING.get(category, 'kitchenware')
        multipliers = self.SEASONAL_MULTIPLIERS.get(seasonal_key, {})
        
        # Get current season multiplier
        multiplier = multipliers.get(current_season, 1.0)
        adjusted_demand = base_demand * multiplier
        
        # Calculate for all seasons
        seasonal_forecast = {}
        for season, mult in multipliers.items():
            seasonal_forecast[season] = round(base_demand * mult, 2)
        
        return {
            'base_demand': round(base_demand, 2),
            'current_season': current_season,
            'seasonal_multiplier': multiplier,
            'adjusted_demand': round(adjusted_demand, 2),
            'seasonal_forecast': seasonal_forecast
        }
    
    def generate_forecast(
        self,
        item_id: Optional[int] = None,
        category: Optional[str] = None,
        hub_id: Optional[int] = None,
        days_forward: int = 30
    ) -> Dict[str, any]:
        """
        Generate complete demand forecast
        
        Args:
            item_id: Specific item ID
            category: Item category
            hub_id: Hub ID
            days_forward: Forecast period
            
        Returns:
            Complete forecast with all adjustments
        """
        # Get historical demand
        historical = self.get_historical_demand(
            item_id=item_id,
            category=category,
            hub_id=hub_id,
            days_back=90
        )
        
        base_demand = historical['daily_average']
        
        # Apply newcomer adjustment
        newcomer_adjusted = self.get_newcomer_adjusted_forecast(
            base_demand=base_demand,
            hub_id=hub_id,
            days_forward=days_forward
        )
        
        # Apply seasonal adjustment
        if category:
            seasonal = self.apply_seasonal_adjustment(
                base_demand=newcomer_adjusted['adjusted_daily_demand'],
                category=category
            )
            final_demand = seasonal['adjusted_demand']
        else:
            seasonal = None
            final_demand = newcomer_adjusted['adjusted_daily_demand']
        
        # Calculate forecast accuracy (based on recent predictions vs actuals)
        accuracy = self._calculate_accuracy(item_id, category, hub_id)
        
        return {
            'forecast_date': timezone.now().isoformat(),
            'forecast_period_days': days_forward,
            'historical_data': historical,
            'newcomer_adjustment': newcomer_adjusted,
            'seasonal_adjustment': seasonal,
            'final_daily_forecast': round(final_demand, 2),
            'final_period_forecast': round(final_demand * days_forward, 1),
            'accuracy_score': accuracy,
            'confidence_level': 'high' if accuracy > 0.8 else 'medium' if accuracy > 0.6 else 'low'
        }
    
    def _calculate_accuracy(
        self,
        item_id: Optional[int],
        category: Optional[str],
        hub_id: Optional[int]
    ) -> float:
        """
        Calculate forecast accuracy based on historical predictions
        For now, return a reasonable estimate based on data availability
        """
        historical = self.get_historical_demand(item_id, category, hub_id, 90)
        
        # More data = higher confidence
        total_reservations = historical['total_reservations']
        
        if total_reservations >= 100:
            return 0.85
        elif total_reservations >= 50:
            return 0.75
        elif total_reservations >= 20:
            return 0.65
        elif total_reservations >= 5:
            return 0.50
        else:
            return 0.35  # Low confidence with little data
    
    def get_high_demand_items(
        self,
        hub_id: Optional[int] = None,
        threshold: float = 0.5
    ) -> List[Dict[str, any]]:
        """
        Identify items with demand exceeding 50% of available inventory
        
        Args:
            hub_id: Hub ID to filter
            threshold: Demand/inventory threshold (default 0.5 = 50%)
            
        Returns:
            List of items with high demand
        """
        query = Q(is_active=True, quantity__gt=0)
        if hub_id:
            query &= Q(hub_id=hub_id)
        
        items = InventoryItem.objects.filter(query)
        high_demand_items = []
        
        for item in items:
            forecast = self.generate_forecast(
                item_id=item.id,
                category=item.category,
                hub_id=hub_id,
                days_forward=30
            )
            
            forecasted_demand = forecast['final_period_forecast']
            current_inventory = item.quantity
            
            # Calculate demand ratio
            demand_ratio = forecasted_demand / current_inventory if current_inventory > 0 else float('inf')
            
            if demand_ratio >= threshold:
                high_demand_items.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'category': item.category,
                    'current_inventory': current_inventory,
                    'forecasted_demand_30days': round(forecasted_demand, 1),
                    'demand_ratio': round(demand_ratio, 2),
                    'forecast_confidence': forecast['confidence_level'],
                    'recommendation': 'urgent' if demand_ratio >= 1.0 else 'moderate'
                })
        
        # Sort by demand ratio (highest first)
        high_demand_items.sort(key=lambda x: x['demand_ratio'], reverse=True)
        
        return high_demand_items


# Singleton instance
_demand_forecaster = None

def get_demand_forecaster() -> DemandForecaster:
    """Get or create demand forecaster singleton"""
    global _demand_forecaster
    if _demand_forecaster is None:
        _demand_forecaster = DemandForecaster()
    return _demand_forecaster
