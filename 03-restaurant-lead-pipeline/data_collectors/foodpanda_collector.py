import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import DELAY_BETWEEN_REQUESTS, TIMEOUT
import sys
import os
# Add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
utils_path = os.path.join(project_root, 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

from windows_timeout import timeout_decorator
from fake_useragent import UserAgent
import json

class FoodPandaCollector:
    def __init__(self):
        self.base_url = "https://www.foodpanda.pk"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.foodpanda.pk/'
        })
        
    @timeout_decorator.timeout(seconds=TIMEOUT)
    def search_restaurants(self, city: str, cuisine_type: str = None) -> List[Dict]:
        """Search for restaurants on FoodPanda in a specific city"""
        restaurants = []
        
        try:
            # FoodPanda city mapping
            city_mapping = self._get_city_mapping(city)
            if not city_mapping:
                print(f"City {city} not found in FoodPanda")
                return restaurants
                
            # Search for restaurants
            search_url = f"{self.base_url}/restaurants"
            params = {
                'city': city_mapping,
                'cuisine': str(cuisine_type).lower() if cuisine_type else ''
            }
            
            response = self.session.get(search_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Parse restaurant listings
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant cards
            restaurant_cards = soup.find_all('div', class_='restaurant-card') or \
                             soup.find_all('div', class_='vendor-card') or \
                             soup.find_all('div', class_='restaurant-item')
            
            for card in restaurant_cards:
                restaurant = self._extract_restaurant_data(card, city)
                if restaurant:
                    restaurants.append(restaurant)
                    
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"Error searching FoodPanda for {city}: {str(e)}")
            
        return restaurants
    
    def _get_city_mapping(self, city: str) -> str:
        """Map city names to FoodPanda city codes"""
        city_mappings = {
            'karachi': 'karachi',
            'lahore': 'lahore',
            'islamabad': 'islamabad',
            'rawalpindi': 'rawalpindi',
            'faisalabad': 'faisalabad',
            'multan': 'multan',
            'peshawar': 'peshawar',
            'quetta': 'quetta',
            'gujranwala': 'gujranwala',
            'sialkot': 'sialkot'
        }
        
        return city_mappings.get(city.lower(), city.lower())
    
    def _extract_restaurant_data(self, card, city: str) -> Optional[Dict]:
        """Extract restaurant data from FoodPanda restaurant card"""
        try:
            # Extract restaurant name
            name = self._extract_text(card, [
                '.restaurant-name', '.vendor-name', '.restaurant-title',
                'h3', 'h4', '.title', '.name'
            ])
            
            if not name:
                return None
                
            # Extract rating
            rating = self._extract_text(card, [
                '.rating', '.restaurant-rating', '.vendor-rating',
                '.stars', '.score'
            ])
            
            # Extract delivery time
            delivery_time = self._extract_text(card, [
                '.delivery-time', '.delivery-duration', '.time',
                '.duration', '.eta'
            ])
            
            # Extract minimum order
            min_order = self._extract_text(card, [
                '.min-order', '.minimum-order', '.min-amount',
                '.order-min', '.min'
            ])
            
            # Extract cuisine types
            cuisines = self._extract_text(card, [
                '.cuisines', '.cuisine-types', '.categories',
                '.tags', '.food-types'
            ])
            
            # Extract restaurant URL
            restaurant_url = self._extract_link(card, [
                'a[href*="/restaurant/"]', 'a[href*="/vendor/"]',
                '.restaurant-link', '.vendor-link'
            ])
            
            # Get detailed information
            details = self._get_restaurant_details(restaurant_url) if restaurant_url else {}
            
            cuisine_type = self._classify_cuisine(name, cuisines)
            
            return {
                'name': name.strip(),
                'city': city,
                'address': details.get('address', ''),
                'phone': details.get('phone', ''),
                'website': restaurant_url,
                'rating': self._parse_rating(rating),
                'reviews_count': details.get('reviews_count', 0),
                'cuisine_type': cuisine_type,
                'location': {'lat': 0, 'lng': 0},
                'place_id': '',
                'source': 'FoodPanda',
                'description': cuisines.strip() if cuisines else '',
                'delivery_time': delivery_time.strip() if delivery_time else '',
                'min_order': min_order.strip() if min_order else '',
                'delivery_fee': details.get('delivery_fee', ''),
                'payment_methods': details.get('payment_methods', [])
            }
            
        except Exception as e:
            print(f"Error extracting FoodPanda restaurant data: {str(e)}")
            return None
    
    def _get_restaurant_details(self, restaurant_url: str) -> Dict:
        """Get detailed information from restaurant page"""
        try:
            response = self.session.get(restaurant_url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract address
            address = self._extract_text(soup, [
                '.restaurant-address', '.vendor-address', '.address',
                '.location', '.restaurant-location'
            ])
            
            # Extract phone
            phone = self._extract_text(soup, [
                '.restaurant-phone', '.vendor-phone', '.phone',
                '.contact-phone', '.business-phone'
            ])
            
            # Extract delivery fee
            delivery_fee = self._extract_text(soup, [
                '.delivery-fee', '.delivery-charge', '.fee',
                '.charge', '.delivery-cost'
            ])
            
            # Extract payment methods
            payment_methods = []
            payment_elements = soup.find_all('span', class_='payment-method') or \
                              soup.find_all('span', class_='payment-type')
            for element in payment_elements:
                payment_methods.append(element.get_text(strip=True))
            
            return {
                'address': address.strip() if address else '',
                'phone': phone.strip() if phone else '',
                'delivery_fee': delivery_fee.strip() if delivery_fee else '',
                'payment_methods': payment_methods,
                'reviews_count': 0  # FoodPanda doesn't show review count on main page
            }
            
        except Exception as e:
            print(f"Error getting FoodPanda restaurant details: {str(e)}")
            return {}
    
    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text using multiple possible selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return ''
    
    def _extract_link(self, element, selectors: List[str]) -> str:
        """Extract link using multiple possible selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.name == 'a':
                return found.get('href', '')
            elif found:
                link = found.find('a')
                if link:
                    return link.get('href', '')
        return ''
    
    def _parse_rating(self, rating_text: str) -> float:
        """Parse rating text to float"""
        try:
            if rating_text:
                # Extract numbers from rating text
                import re
                numbers = re.findall(r'\d+\.?\d*', rating_text)
                if numbers:
                    return float(numbers[0])
            return 0.0
        except:
            return 0.0
    
    def _classify_cuisine(self, name: str, cuisines: str) -> str:
        """Classify cuisine type based on name and cuisines"""
        text = f"{name} {cuisines}".lower()
        
        cuisine_keywords = {
            'bbq': 'BBQ',
            'grill': 'BBQ',
            'chinese': 'Chinese',
            'thai': 'Thai',
            'italian': 'Italian',
            'pizza': 'Italian',
            'pasta': 'Italian',
            'mexican': 'Mexican',
            'taco': 'Mexican',
            'japanese': 'Japanese',
            'sushi': 'Japanese',
            'korean': 'Korean',
            'indian': 'Indian',
            'curry': 'Indian',
            'burger': 'Fast Food',
            'fast food': 'Fast Food',
            'cafe': 'Beverages',
            'coffee': 'Beverages',
            'tea': 'Beverages',
            'dessert': 'Desserts',
            'ice cream': 'Desserts',
            'bakery': 'Desserts'
        }
        
        for keyword, cuisine in cuisine_keywords.items():
            if keyword in text:
                return cuisine
                
        return 'Pakistani'  # Default 