"""Utility functions for user management."""
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging

logger = logging.getLogger(__name__)


def geocode_address(address: str) -> Point | None:
    """
    Convert an address string to geographic coordinates.
    
    Args:
        address: The address string to geocode
        
    Returns:
        Point object with longitude and latitude, or None if geocoding fails
    """
    if not address or not address.strip():
        return None
    
    try:
        geolocator = Nominatim(user_agent="flokr_platform")
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            # Point takes (longitude, latitude) - note the order!
            return Point(location.longitude, location.latitude)
        else:
            logger.warning(f"Could not geocode address: {address}")
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logger.error(f"Geocoding error for address '{address}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error geocoding address '{address}': {str(e)}")
        return None


def find_nearest_hub(user):
    """
    Find and assign the nearest hub to a user based on their location.
    
    Args:
        user: User instance with a location field
        
    Returns:
        Hub instance or None if no hubs exist or user has no location
    """
    if not user.location:
        return None
    
    from hubs.models import Hub
    from django.contrib.gis.db.models.functions import Distance
    
    try:
        nearest_hub = Hub.objects.annotate(
            distance=Distance('location', user.location)
        ).order_by('distance').first()
        
        return nearest_hub
    except Exception as e:
        logger.error(f"Error finding nearest hub for user {user.id}: {str(e)}")
        return None
