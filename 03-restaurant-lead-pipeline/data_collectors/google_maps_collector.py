import time
import json
import requests
from typing import List, Dict, Optional
from config import GOOGLE_MAPS_API_KEY, DELAY_BETWEEN_REQUESTS, TIMEOUT
import sys
import os
# Add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
utils_path = os.path.join(project_root, 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

from windows_timeout import timeout_decorator

class GoogleMapsCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
    @timeout_decorator.timeout(seconds=TIMEOUT)
    def search_restaurants(self, city: str, cuisine_type: str = None) -> List[Dict]:
        """Search for restaurants in a specific city using Google Places API"""
        restaurants = []
        
        # Search query
        query = f"restaurants in {city}, Pakistan"
        if cuisine_type:
            query += f" {cuisine_type}"
            
        # Text Search API
        search_url = f"{self.base_url}/textsearch/json"
        params = {
            'query': query,
            'key': self.api_key,
            'region': 'pk',  # Pakistan
            'type': 'restaurant'
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'OK':
                for place in data['results']:
                    restaurant = self._extract_restaurant_data(place, city)
                    if restaurant:
                        restaurants.append(restaurant)
                        
            # Get additional details for each restaurant
            for restaurant in restaurants:
                if restaurant.get('place_id'):
                    details = self._get_place_details(restaurant['place_id'])
                    if details:
                        restaurant.update(details)
                        
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"Error searching restaurants in {city}: {str(e)}")
            
        return restaurants
    
    def _extract_restaurant_data(self, place: Dict, city: str) -> Optional[Dict]:
        """Extract relevant restaurant data from Google Places API response"""
        try:
            return {
                'name': place.get('name', ''),
                'city': city,
                'address': place.get('formatted_address', ''),
                'phone': '',  # Will be filled by place details
                'website': '',  # Will be filled by place details
                'rating': place.get('rating', 0),
                'reviews_count': place.get('user_ratings_total', 0),
                'cuisine_type': self._extract_cuisine_type(place),
                'location': {
                    'lat': place.get('geometry', {}).get('location', {}).get('lat', 0),
                    'lng': place.get('geometry', {}).get('location', {}).get('lng', 0)
                },
                'place_id': place.get('place_id', ''),
                'source': 'Google Maps'
            }
        except Exception as e:
            print(f"Error extracting restaurant data: {str(e)}")
            return None
    
    def _extract_cuisine_type(self, place: Dict) -> str:
        """Extract cuisine type from place types or name"""
        types = place.get('types', [])
        name = place.get('name', '').lower()
        
        # Check types first
        cuisine_keywords = {
            'restaurant': 'Pakistani',
            'chinese_restaurant': 'Chinese',
            'indian_restaurant': 'Indian',
            'italian_restaurant': 'Italian',
            'thai_restaurant': 'Thai',
            'mexican_restaurant': 'Mexican',
            'japanese_restaurant': 'Japanese',
            'korean_restaurant': 'Korean',
            'fast_food': 'Fast Food',
            'cafe': 'Beverages'
        }
        
        for place_type, cuisine in cuisine_keywords.items():
            if place_type in types:
                return cuisine
        
        # Check name for keywords
        name_keywords = {
            'bbq': 'BBQ',
            'grill': 'BBQ',
            'pizza': 'Italian',
            'burger': 'Fast Food',
            'chinese': 'Chinese',
            'thai': 'Thai',
            'mexican': 'Mexican',
            'japanese': 'Japanese',
            'korean': 'Korean',
            'dessert': 'Desserts',
            'ice cream': 'Desserts',
            'coffee': 'Beverages',
            'tea': 'Beverages'
        }
        
        for keyword, cuisine in name_keywords.items():
            if keyword in name:
                return cuisine
                
        return 'Pakistani'  # Default
    
    @timeout_decorator.timeout(seconds=TIMEOUT)
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a specific place"""
        details_url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'formatted_phone_number,website,opening_hours,price_level'
        }
        
        try:
            response = requests.get(details_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'OK':
                place = data['result']
                return {
                    'phone': place.get('formatted_phone_number', ''),
                    'website': place.get('website', ''),
                    'opening_hours': place.get('opening_hours', {}).get('weekday_text', []),
                    'price_level': place.get('price_level', 0)
                }
                
        except Exception as e:
            print(f"Error getting place details: {str(e)}")
            
        return None 