import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

# Pakistan Cities for targeted search (expanded list)
PAKISTAN_CITIES = [
    'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad',
    'Multan', 'Peshawar', 'Quetta', 'Gujranwala', 'Sialkot',
    'Bahawalpur', 'Sargodha', 'Jhang', 'Sheikhupura', 'Rahim Yar Khan',
    'Gujrat', 'Kasur', 'Okara', 'Mianwali', 'Sahiwal',
    'Mandi Bahauddin', 'Khanewal', 'Vehari', 'Dera Ghazi Khan',
    'Muzaffargarh', 'Layyah', 'Bhakkar', 'Khushab', 'Chiniot',
    'Hafizabad', 'Narowal', 'Gujar Khan', 'Taxila', 'Murree',
    'Attock', 'Jhelum', 'Chakwal', 'Talagang', 'Kallar Kahar'
]

# Cuisine types for classification (expanded)
CUISINE_TYPES = [
    'Pakistani', 'BBQ', 'Chinese', 'Fast Food', 'Italian', 'Thai',
    'Indian', 'Turkish', 'Lebanese', 'Mexican', 'Japanese', 'Korean',
    'American', 'European', 'Fusion', 'Desserts', 'Beverages',
    'Seafood', 'Steakhouse', 'Pizza', 'Burgers', 'Sandwiches',
    'Ice Cream', 'Coffee', 'Tea', 'Juice', 'Smoothies', 'Bakery',
    'Street Food', 'Traditional', 'Modern', 'Vegan', 'Vegetarian'
]

# Enhanced search parameters for 5k+ leads per source
MAX_RESTAURANTS_PER_CITY = 500  # Increased from 100
MAX_RESTAURANTS_PER_SOURCE = 5000  # New target per source
DELAY_BETWEEN_REQUESTS = 1  # Reduced from 2 seconds for faster collection
TIMEOUT = 45  # Increased timeout for larger requests
BATCH_SIZE = 100  # Process data in batches for better performance

# ML Model Configuration
ML_CONFIG = {
    'cuisine_classifier': {
        'model_type': 'random_forest',  # Better than naive bayes
        'max_features': 5000,
        'n_estimators': 200,
        'random_state': 42
    },
    'lead_scorer': {
        'model_type': 'gradient_boosting',
        'n_estimators': 300,
        'learning_rate': 0.1,
        'max_depth': 8,
        'random_state': 42
    }
}

# Output settings
OUTPUT_CSV = 'pakistan_restaurant_leads.csv'
OUTPUT_EXCEL = 'pakistan_restaurant_leads.xlsx'
OUTPUT_JSON = 'pakistan_restaurant_leads.json'

# Data Quality Thresholds
MIN_LEAD_SCORE = 50  # Minimum score for high-quality leads
MIN_DATA_COMPLETENESS = 70  # Minimum data completeness percentage 