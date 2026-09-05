import random
import time
from typing import List, Dict
from config import PAKISTAN_CITIES, CUISINE_TYPES

class DemoCollector:
    """Enhanced demo data collector that generates realistic sample restaurant data"""
    
    def __init__(self, source_name: str = "Demo"):
        self.source_name = source_name
        self.restaurant_names = self._load_restaurant_names()
        self.local_restaurant_names = self._load_local_restaurant_names()
        
    def _load_restaurant_names(self) -> List[str]:
        """Load international restaurant names"""
        return [
            "BBQ Tonight", "Chinese Wok", "Pizza Hut", "KFC", "McDonald's",
            "Subway", "Domino's", "Hardee's", "Burger King", "Pizza Express",
            "Taco Bell", "Wendy's", "Popeyes", "Dunkin'", "Starbucks",
            "Gloria Jean's", "Second Cup", "Tim Hortons", "Costa Coffee",
            "Nando's", "TGI Fridays", "Chili's", "Applebee's", "Buffalo Wild Wings",
            "Red Lobster", "Olive Garden", "Outback Steakhouse", "LongHorn Steakhouse",
            "Texas Roadhouse", "Cracker Barrel", "IHOP", "Denny's", "Waffle House",
            "Chipotle", "Qdoba", "Moe's Southwest Grill", "Panera Bread",
            "Five Guys", "Shake Shack", "In-N-Out Burger", "Whataburger",
            "Culver's", "Steak 'n Shake", "Jack in the Box", "Carl's Jr.",
            "Sonic Drive-In", "Arby's", "Dairy Queen", "Baskin-Robbins",
            "Cold Stone Creamery", "Ben & Jerry's", "Haagen-Dazs"
        ]
    
    def _load_local_restaurant_names(self) -> List[str]:
        """Load local Pakistani restaurant names"""
        return [
            "Karachi Darbar", "Lahore Karahi", "Islamabad BBQ", "Peshawar Tikka",
            "Multan Handi", "Quetta Sajji", "Faisalabad Fish", "Sialkot Biryani",
            "Gujranwala Nihari", "Bahawalpur Korma", "Sargodha Pulao",
            "Jhang Karahi", "Sheikhupura BBQ", "Rahim Yar Khan Fish",
            "Gujrat Tikka", "Kasur Biryani", "Okara Handi", "Mianwali Sajji",
            "Sahiwal Korma", "Mandi Bahauddin Pulao", "Khanewal Karahi",
            "Vehari BBQ", "Dera Ghazi Khan Fish", "Muzaffargarh Tikka",
            "Layyah Biryani", "Bhakkar Handi", "Khushab Sajji",
            "Chiniot Korma", "Hafizabad Pulao", "Narowal Karahi",
            "Gujar Khan BBQ", "Taxila Fish", "Murree Tikka", "Attock Biryani",
            "Jhelum Handi", "Chakwal Sajji", "Talagang Korma", "Kallar Kahar Pulao"
        ]
    
    def search_restaurants(self, city: str, max_per_city: int = 100) -> List[Dict]:
        """Generate sample restaurant data for a city with enhanced capacity"""
        restaurants = []
        # Generate more restaurants for larger cities
        if city in ['Karachi', 'Lahore', 'Islamabad']:
            num_restaurants = min(max_per_city, random.randint(80, 120))
        elif city in ['Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar']:
            num_restaurants = min(max_per_city, random.randint(60, 90))
        else:
            num_restaurants = min(max_per_city, random.randint(40, 70))
        
        for i in range(num_restaurants):
            restaurant = self._generate_restaurant(city, i)
            restaurants.append(restaurant)
            
            # Small delay to simulate real collection
            time.sleep(0.05)  # Reduced delay for faster generation
        
        return restaurants
    
    def _generate_restaurant(self, city: str, index: int) -> Dict:
        """Generate a single restaurant record with enhanced variety"""
        # Mix local and international names
        if random.random() > 0.6:
            name = random.choice(self.local_restaurant_names)
            if index > 0:
                name += f" {city} Branch {index + 1}"
        else:
            name = random.choice(self.restaurant_names)
            if index > 0:
                name += f" {city} Branch {index + 1}"
        
        # Select cuisine type with weighted distribution
        cuisine = self._select_cuisine_type()
        
        # Generate phone number
        phone = self._generate_phone_number(city)
        
        # Generate address
        address = self._generate_address(city)
        
        # Generate rating with more realistic distribution
        rating = self._generate_rating()
        
        # Generate review count based on rating
        reviews_count = self._generate_review_count(rating)
        
        # Generate website (70% chance for better data quality)
        website = ""
        if random.random() > 0.3:
            website = f"https://www.{name.lower().replace(' ', '').replace('&', 'and').replace('-', '')}.com"
        
        # Generate social media (60% chance)
        social_media = {}
        if random.random() > 0.4:
            social_media = {
                'facebook': f"https://facebook.com/{name.lower().replace(' ', '')}",
                'instagram': f"https://instagram.com/{name.lower().replace(' ', '')}",
                'twitter': f"https://twitter.com/{name.lower().replace(' ', '')}"
            }
        
        # Generate lead score based on data quality
        lead_score = self._calculate_lead_score(rating, reviews_count, website, social_media)
        
        return {
            'name': name,
            'city': city,
            'cuisine_type': cuisine,
            'phone': phone,
            'address': address,
            'website': website,
            'rating': rating,
            'reviews_count': reviews_count,
            'source': self.source_name,
            'social_media': social_media,
            'description': f"Delicious {cuisine} cuisine in {city}. Rated {rating}/5 stars with {reviews_count} reviews.",
            'lead_score': lead_score,
            'lead_potential': self._categorize_lead_potential(lead_score)
        }
    
    def _select_cuisine_type(self) -> str:
        """Select cuisine type with weighted distribution"""
        # Pakistani and BBQ are more common in Pakistan
        cuisine_weights = {
            'Pakistani': 0.25,
            'BBQ': 0.20,
            'Fast Food': 0.15,
            'Chinese': 0.10,
            'Indian': 0.08,
            'Italian': 0.06,
            'Desserts': 0.05,
            'Beverages': 0.05,
            'Other': 0.06
        }
        
        rand = random.random()
        cumulative = 0
        for cuisine, weight in cuisine_weights.items():
            cumulative += weight
            if rand <= cumulative:
                if cuisine == 'Other':
                    return random.choice(['Thai', 'Turkish', 'Lebanese', 'Mexican', 'Japanese', 'Korean', 'American', 'European'])
                return cuisine
        
        return 'Pakistani'  # Default fallback
    
    def _generate_rating(self) -> float:
        """Generate realistic rating distribution"""
        # Most restaurants have 3.5-4.5 ratings
        rand = random.random()
        if rand < 0.1:  # 10% chance of low rating
            return round(random.uniform(2.5, 3.4), 1)
        elif rand < 0.8:  # 70% chance of good rating
            return round(random.uniform(3.5, 4.4), 1)
        else:  # 20% chance of excellent rating
            return round(random.uniform(4.5, 5.0), 1)
    
    def _generate_review_count(self, rating: float) -> int:
        """Generate review count based on rating"""
        if rating < 3.0:
            return random.randint(5, 50)  # Fewer reviews for low-rated places
        elif rating < 4.0:
            return random.randint(20, 200)  # Moderate reviews
        else:
            return random.randint(100, 1000)  # Many reviews for highly-rated places
    
    def _calculate_lead_score(self, rating: float, reviews_count: int, website: str, social_media: dict) -> float:
        """Calculate lead score based on data quality"""
        score = 0
        
        # Rating contribution (0-40 points)
        score += (rating - 1) * 10
        
        # Reviews contribution (0-30 points)
        if reviews_count > 500:
            score += 30
        elif reviews_count > 100:
            score += 20
        elif reviews_count > 50:
            score += 15
        elif reviews_count > 10:
            score += 10
        
        # Website contribution (0-15 points)
        if website:
            score += 15
        
        # Social media contribution (0-15 points)
        if social_media:
            score += min(len(social_media) * 5, 15)
        
        return min(score, 100)  # Cap at 100
    
    def _categorize_lead_potential(self, lead_score: float) -> str:
        """Categorize lead potential based on score"""
        if lead_score >= 80:
            return "High"
        elif lead_score >= 60:
            return "Medium"
        elif lead_score >= 40:
            return "Low"
        else:
            return "Poor"
    
    def _generate_phone_number(self, city: str) -> str:
        """Generate realistic phone number based on city"""
        city_codes = {
            'Karachi': ['021', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Lahore': ['042', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Islamabad': ['051', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Rawalpindi': ['051', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Faisalabad': ['041', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Multan': ['061', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Peshawar': ['091', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Quetta': ['081', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Gujranwala': ['055', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Sialkot': ['052', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Bahawalpur': ['062', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Sargodha': ['048', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Jhang': ['047', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Sheikhupura': ['056', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Rahim Yar Khan': ['068', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Gujrat': ['053', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Kasur': ['049', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Okara': ['044', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Mianwali': ['045', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Sahiwal': ['040', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Mandi Bahauddin': ['054', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Khanewal': ['065', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Vehari': ['067', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Dera Ghazi Khan': ['064', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Muzaffargarh': ['066', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Layyah': ['060', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Bhakkar': ['063', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Khushab': ['046', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Chiniot': ['043', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Hafizabad': ['057', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Narowal': ['058', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Gujar Khan': ['059', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Taxila': ['059', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Murree': ['059', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Attock': ['057', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Jhelum': ['054', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Chakwal': ['054', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Talagang': ['054', '0300', '0301', '0302', '0303', '0304', '0305'],
            'Kallar Kahar': ['054', '0300', '0301', '0302', '0303', '0304', '0305']
        }
        
        city_code = random.choice(city_codes.get(city, ['0300', '0301', '0302']))
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        
        return f"+92 {city_code} {number[:3]} {number[3:5]} {number[5:]}"
    
    def _generate_address(self, city: str) -> str:
        """Generate realistic address for a city"""
        areas = {
            'Karachi': ['Clifton', 'Defence', 'Gulshan-e-Iqbal', 'North Nazimabad', 'Malir', 'Korangi', 'Saddar', 'Lyari', 'Orangi', 'Gulistan-e-Jauhar', 'Landhi', 'Korangi', 'Shah Faisal', 'Airport', 'Port Grand'],
            'Lahore': ['Gulberg', 'Defence', 'Johar Town', 'Model Town', 'Cantt', 'Old City', 'Anarkali', 'Shah Alam', 'Data Ganj', 'Mall Road', 'Liberty Market', 'DHA Phase 1', 'DHA Phase 2', 'DHA Phase 3', 'DHA Phase 4'],
            'Islamabad': ['F-7', 'F-8', 'E-7', 'E-8', 'G-7', 'G-8', 'Blue Area', 'Sector F-6', 'Sector G-6', 'Sector H-8', 'Sector I-8', 'Sector I-9', 'Sector I-10', 'Sector I-11', 'Sector I-12'],
            'Rawalpindi': ['Cantt', 'Raja Bazar', 'Saddar', 'Westridge', 'Bahria Town', 'DHA', 'Chaklala', 'Peshawar Road', 'Murree Road', 'Grand Trunk Road', 'Saddar Bazar', 'Commercial Market', 'Bank Road', 'Mall Road'],
            'Faisalabad': ['Cantt', 'D Ground', 'Jinnah Colony', 'Madina Town', 'Lyallpur', 'Gulberg', 'Samundri Road', 'Sargodha Road', 'Lahore Road', 'Multan Road', 'Railway Road', 'Batala Colony', 'Peoples Colony', 'Satiana Road'],
            'Multan': ['Cantt', 'Ghanta Ghar', 'Haram Gate', 'Bosan Road', 'Vehari Road', 'Nawan Shehr', 'Daulat Gate', 'Pak Gate', 'Delhi Gate', 'Lohari Gate', 'Qasim Bela', 'Shah Rukn-e-Alam', 'Mumtaz Mahal', 'Tomb of Shah Rukn-e-Alam'],
            'Peshawar': ['Cantt', 'University Town', 'Hayatabad', 'Gulbahar', 'Sadar', 'Namak Mandi', 'Qissa Khwani', 'Bara Road', 'Ring Road', 'University Road', 'Grand Trunk Road', 'Jamrud Road', 'Charsadda Road', 'Mardan Road'],
            'Quetta': ['Cantt', 'Jinnah Road', 'Prince Road', 'Sariab Road', 'Brewery Road', 'Hanna Valley', 'Spinny Road', 'Zarghun Road', 'Mastung Road', 'Chiltan Road', 'Brewery Road', 'Hanna Valley', 'Spinny Road', 'Zarghun Road'],
            'Gujranwala': ['Cantt', 'G.T. Road', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Sialkot Bypass', 'Lahore Road', 'Sialkot Road', 'Gujrat Road', 'Wazirabad Road', 'Chenab Road', 'Ravi Road', 'Sutlej Road', 'Beas Road'],
            'Sialkot': ['Cantt', 'Allama Iqbal Road', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Sambrial Road', 'Gujranwala Road', 'Lahore Road', 'Narowal Road', 'Zafarwal Road', 'Daska Road', 'Pasrur Road', 'Chawinda Road', 'Qila Kalarwala Road']
        }
        
        # Add more cities with realistic areas
        for other_city in ['Bahawalpur', 'Sargodha', 'Jhang', 'Sheikhupura', 'Rahim Yar Khan', 'Gujrat', 'Kasur', 'Okara', 'Mianwali', 'Sahiwal', 'Mandi Bahauddin', 'Khanewal', 'Vehari', 'Dera Ghazi Khan', 'Muzaffargarh', 'Layyah', 'Bhakkar', 'Khushab', 'Chiniot', 'Hafizabad', 'Narowal', 'Gujar Khan', 'Taxila', 'Murree', 'Attock', 'Jhelum', 'Chakwal', 'Talagang', 'Kallar Kahar']:
            if other_city not in areas:
                areas[other_city] = ['Main Area', 'City Center', 'Commercial District', 'Market Area', 'Residential Area', 'Industrial Area', 'University Area', 'Hospital Area', 'Station Area', 'Airport Area']
        
        area = random.choice(areas.get(city, ['Main Area', 'City Center', 'Commercial District']))
        street = random.choice(['Main Street', 'Commercial Avenue', 'Business Road', 'Market Street', 'Mall Road', 'Station Road', 'University Road', 'Hospital Road', 'Airport Road', 'Port Road', 'Canal Road', 'Bridge Road', 'Highway Road', 'Expressway Road'])
        number = random.randint(1, 100)
        
        return f"{number} {street}, {area}, {city}"
