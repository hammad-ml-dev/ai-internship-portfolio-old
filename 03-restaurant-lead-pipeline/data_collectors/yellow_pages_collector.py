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

class YellowPagesCollector:
    def __init__(self):
        self.base_url = "https://yellowpages.pk"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    @timeout_decorator.timeout(seconds=TIMEOUT)
    def search_restaurants(self, city: str, cuisine_type: str = None) -> List[Dict]:
        """Search for restaurants in Yellow Pages Pakistan"""
        restaurants = []
        
        try:
            # Search for restaurants in the city
            search_query = f"restaurants in {city}"
            if cuisine_type:
                search_query += f" {cuisine_type}"
                
            # Construct search URL
            search_url = f"{self.base_url}/search"
            params = {
                'q': search_query,
                'location': city,
                'category': 'restaurants'
            }
            
            response = self.session.get(search_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Parse the search results
            soup = BeautifulSoup(response.content, 'html.parser')
            restaurant_cards = soup.find_all('div', class_='listing-card') or \
                             soup.find_all('div', class_='business-listing') or \
                             soup.find_all('div', class_='result-item')
            
            for card in restaurant_cards:
                restaurant = self._extract_restaurant_data(card, city)
                if restaurant:
                    restaurants.append(restaurant)
                    
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"Error searching Yellow Pages for {city}: {str(e)}")
            
        return restaurants
    
    def _extract_restaurant_data(self, card, city: str) -> Optional[Dict]:
        """Extract restaurant data from Yellow Pages listing card"""
        try:
            # Try different possible selectors for Yellow Pages
            name = self._extract_text(card, [
                '.business-name', '.listing-name', '.company-name',
                'h3', 'h4', '.title', '.name'
            ])
            
            if not name:
                return None
                
            address = self._extract_text(card, [
                '.address', '.location', '.street-address',
                '.business-address', '.contact-info'
            ])
            
            phone = self._extract_text(card, [
                '.phone', '.telephone', '.contact-phone',
                '.business-phone', '.phone-number'
            ])
            
            website = self._extract_link(card, [
                '.website', '.web-link', '.business-website',
                'a[href*="http"]'
            ])
            
            # Extract cuisine type from description or name
            description = self._extract_text(card, [
                '.description', '.business-description', '.summary',
                '.category', '.business-category'
            ])
            
            cuisine_type = self._classify_cuisine(name, description)
            
            return {
                'name': name.strip(),
                'city': city,
                'address': address.strip() if address else '',
                'phone': phone.strip() if phone else '',
                'website': website,
                'rating': 0,  # Yellow Pages doesn't typically have ratings
                'reviews_count': 0,
                'cuisine_type': cuisine_type,
                'location': {'lat': 0, 'lng': 0},  # Not available in Yellow Pages
                'place_id': '',
                'source': 'Yellow Pages PK',
                'description': description.strip() if description else ''
            }
            
        except Exception as e:
            print(f"Error extracting restaurant data from Yellow Pages: {str(e)}")
            return None
    
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
                # Look for links within the element
                link = found.find('a')
                if link:
                    return link.get('href', '')
        return ''
    
    def _classify_cuisine(self, name: str, description: str) -> str:
        """Classify cuisine type based on name and description"""
        text = f"{name} {description}".lower()
        
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