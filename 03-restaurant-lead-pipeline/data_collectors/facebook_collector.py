import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import FACEBOOK_ACCESS_TOKEN, DELAY_BETWEEN_REQUESTS, TIMEOUT
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

class FacebookCollector:
    def __init__(self, access_token: str = None):
        self.access_token = access_token
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
        """Search for restaurant Facebook pages in a specific city"""
        restaurants = []
        
        try:
            # Search query for Facebook
            search_query = f"restaurants {city} Pakistan"
            if cuisine_type:
                search_query += f" {cuisine_type}"
                
            # Facebook search URL
            search_url = "https://www.facebook.com/search/pages/"
            params = {
                'q': search_query,
                'filters': 'eyJycF9jaXR5Ijoie1wibmFtZVwiOlwiY2l0eVwiLFwiYXJnc1wiOlwiXCJ9In0%3D',
                'type': 'pages'
            }
            
            response = self.session.get(search_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Parse Facebook search results
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for page results
            page_results = soup.find_all('div', {'data-testid': 'page-result'}) or \
                          soup.find_all('div', class_='page-result') or \
                          soup.find_all('div', class_='search-result')
            
            for result in page_results:
                restaurant = self._extract_page_data(result, city)
                if restaurant:
                    restaurants.append(restaurant)
                    
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"Error searching Facebook for {city}: {str(e)}")
            
        return restaurants
    
    def _extract_page_data(self, result, city: str) -> Optional[Dict]:
        """Extract restaurant data from Facebook page result"""
        try:
            # Extract page name
            name = self._extract_text(result, [
                '[data-testid="page-title"]', '.page-title', '.page-name',
                'h3', 'h4', '.title', '.name'
            ])
            
            if not name:
                return None
                
            # Extract page URL
            page_url = self._extract_link(result, [
                'a[href*="/pages/"]', 'a[href*="facebook.com"]',
                '.page-link', '.page-url'
            ])
            
            # Extract description/category
            description = self._extract_text(result, [
                '.page-description', '.page-category', '.page-summary',
                '.description', '.category'
            ])
            
            # Extract follower count
            followers = self._extract_text(result, [
                '.page-followers', '.followers-count', '.likes-count',
                '.page-likes', '.followers'
            ])
            
            cuisine_type = self._classify_cuisine(name, description)
            
            return {
                'name': name.strip(),
                'city': city,
                'address': '',  # Not available in search results
                'phone': '',  # Not available in search results
                'website': page_url,
                'rating': 0,  # Not available in search results
                'reviews_count': 0,
                'cuisine_type': cuisine_type,
                'location': {'lat': 0, 'lng': 0},
                'place_id': '',
                'source': 'Facebook Pages',
                'description': description.strip() if description else '',
                'followers': followers.strip() if followers else '',
                'social_media': {
                    'facebook': page_url,
                    'instagram': '',
                    'twitter': ''
                }
            }
            
        except Exception as e:
            print(f"Error extracting Facebook page data: {str(e)}")
            return None
    
    def get_page_details(self, page_url: str) -> Optional[Dict]:
        """Get detailed information from a Facebook page"""
        try:
            response = self.session.get(page_url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract additional details
            phone = self._extract_text(soup, [
                '[data-testid="page-phone"]', '.page-phone', '.phone-number',
                '.contact-phone', '.business-phone'
            ])
            
            address = self._extract_text(soup, [
                '[data-testid="page-address"]', '.page-address', '.address',
                '.business-address', '.location'
            ])
            
            website = self._extract_link(soup, [
                'a[href*="http"][href*="facebook.com"]:not([href*="/pages/"])',
                '.page-website', '.website-link', '.business-website'
            ])
            
            return {
                'phone': phone.strip() if phone else '',
                'address': address.strip() if address else '',
                'website': website
            }
            
        except Exception as e:
            print(f"Error getting Facebook page details: {str(e)}")
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