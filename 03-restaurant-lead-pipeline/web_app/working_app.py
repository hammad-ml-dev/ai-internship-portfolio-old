from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
import sys
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)
CORS(app)

# Pakistan Cities for targeted search
PAKISTAN_CITIES = [
    'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad',
    'Multan', 'Peshawar', 'Quetta', 'Gujranwala', 'Sialkot',
    'Bahawalpur', 'Sargodha', 'Jhang', 'Sheikhupura', 'Rahim Yar Khan',
    'Gujrat', 'Kasur', 'Okara', 'Mianwali', 'Sahiwal'
]

# Cuisine types for classification
CUISINE_TYPES = [
    'Pakistani', 'BBQ', 'Chinese', 'Fast Food', 'Italian', 'Thai',
    'Indian', 'Turkish', 'Lebanese', 'Mexican', 'Japanese', 'Korean',
    'American', 'European', 'Fusion', 'Desserts', 'Beverages'
]

# Global variables for data storage
current_data = []
collection_status = "idle"
collection_progress = 0
collection_message = ""

class DemoCollector:
    """Demo data collector that generates realistic sample restaurant data"""
    
    def __init__(self, source_name: str = "Demo"):
        self.source_name = source_name
        self.restaurant_names = [
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

    def search_restaurants(self, city: str, max_per_city: int = 20):
        """Generate sample restaurant data for a city"""
        restaurants = []
        num_restaurants = min(max_per_city, random.randint(15, 25))

        for i in range(num_restaurants):
            restaurant = self._generate_restaurant(city, i)
            restaurants.append(restaurant)
            time.sleep(0.1)  # Small delay to simulate real collection

        return restaurants

    def _generate_restaurant(self, city: str, index: int):
        """Generate a single restaurant record"""
        name = random.choice(self.restaurant_names)
        if index > 0:
            name += f" {city} Branch {index + 1}"

        cuisine = random.choice(CUISINE_TYPES)
        phone = self._generate_phone_number(city)
        address = self._generate_address(city)
        rating = round(random.uniform(3.0, 5.0), 1)
        reviews_count = random.randint(10, 500)
        
        website = ""
        if random.random() > 0.5:
            website = f"https://www.{name.lower().replace(' ', '').replace('&', 'and')}.com"

        social_media = {}
        if random.random() > 0.7:
            social_media = {
                'facebook': f"https://facebook.com/{name.lower().replace(' ', '')}",
                'instagram': f"https://instagram.com/{name.lower().replace(' ', '')}",
                'twitter': f"https://twitter.com/{name.lower().replace(' ', '')}"
            }

        # Generate lead score based on rating and reviews
        lead_score = round((rating * 0.6) + (min(reviews_count, 1000) / 1000 * 0.4), 2)
        lead_potential = "High" if lead_score > 4.0 else "Medium" if lead_score > 3.0 else "Low"

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
            'lead_potential': lead_potential
        }

    def _generate_phone_number(self, city: str):
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
            'Sahiwal': ['040', '0300', '0301', '0302', '0303', '0304', '0305']
        }

        city_code = random.choice(city_codes.get(city, ['0300', '0301', '0302']))
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"+92 {city_code} {number[:3]} {number[3:5]} {number[5:]}"

    def _generate_address(self, city: str):
        """Generate realistic address for a city"""
        areas = {
            'Karachi': ['Clifton', 'Defence', 'Gulshan-e-Iqbal', 'North Nazimabad', 'Malir', 'Korangi', 'Saddar', 'Lyari', 'Orangi'],
            'Lahore': ['Gulberg', 'Defence', 'Johar Town', 'Model Town', 'Cantt', 'Old City', 'Anarkali', 'Shah Alam', 'Data Ganj'],
            'Islamabad': ['F-7', 'F-8', 'E-7', 'E-8', 'G-7', 'G-8', 'Blue Area', 'Sector F-6', 'Sector G-6'],
            'Rawalpindi': ['Cantt', 'Raja Bazar', 'Saddar', 'Westridge', 'Bahria Town', 'DHA', 'Chaklala', 'Peshawar Road'],
            'Faisalabad': ['Cantt', 'D Ground', 'Jinnah Colony', 'Madina Town', 'Lyallpur', 'Gulberg', 'Samundri Road'],
            'Multan': ['Cantt', 'Ghanta Ghar', 'Haram Gate', 'Bosan Road', 'Vehari Road', 'Nawan Shehr', 'Daulat Gate'],
            'Peshawar': ['Cantt', 'University Town', 'Hayatabad', 'Gulbahar', 'Sadar', 'Namak Mandi', 'Qissa Khwani'],
            'Quetta': ['Cantt', 'Jinnah Road', 'Prince Road', 'Sariab Road', 'Brewery Road', 'Hanna Valley', 'Spinny Road'],
            'Gujranwala': ['Cantt', 'G.T. Road', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Sialkot Bypass'],
            'Sialkot': ['Cantt', 'Allama Iqbal Road', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Sambrial Road'],
            'Bahawalpur': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Multan Road', 'Ahmadpur Road'],
            'Sargodha': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Faisalabad Road', 'Jhang Road'],
            'Jhang': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Faisalabad Road', 'Multan Road'],
            'Sheikhupura': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Lahore Road', 'Gujranwala Road'],
            'Rahim Yar Khan': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Multan Road', 'Bahawalpur Road'],
            'Gujrat': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Gujranwala Road', 'Sialkot Road'],
            'Kasur': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Lahore Road', 'Ferozepur Road'],
            'Okara': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Lahore Road', 'Faisalabad Road'],
            'Mianwali': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Sargodha Road', 'Kalabagh Road'],
            'Sahiwal': ['Cantt', 'Model Town', 'Civil Lines', 'Raja Bazar', 'Lahore Road', 'Multan Road']
        }

        area = random.choice(areas.get(city, ['Main Area', 'City Center', 'Commercial District']))
        street = random.choice(['Main Street', 'Commercial Avenue', 'Business Road', 'Market Street', 'Mall Road', 'Station Road'])
        number = random.randint(1, 100)
        return f"{number} {street}, {area}, {city}"

class WebPipeline:
    def __init__(self):
        self.collectors = {}
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize pipeline components"""
        try:
            self.collectors['yellow_pages'] = DemoCollector("Yellow Pages PK")
            self.collectors['foodpanda'] = DemoCollector("FoodPanda")
            self.collectors['google_maps'] = DemoCollector("Google Maps")
            self.collectors['facebook_pages'] = DemoCollector("Facebook Pages")
            print("✓ Pipeline initialized successfully")
        except Exception as e:
            print(f"⚠ Pipeline initialization failed: {e}")
    
    def collect_data(self, cities, sources, max_per_city):
        """Collect restaurant data from selected sources"""
        global current_data, collection_status, collection_progress, collection_message
        
        collection_status = "collecting"
        collection_progress = 0
        collection_message = "Starting data collection..."
        
        all_restaurants = []
        total_cities = len(cities)
        
        for i, city in enumerate(cities):
            collection_message = f"Collecting data for {city}..."
            collection_progress = (i / total_cities) * 50
            
            city_restaurants = []
            
            for source_name in sources:
                if source_name in self.collectors:
                    try:
                        collection_message = f"Searching {source_name} for {city}..."
                        restaurants = self.collectors[source_name].search_restaurants(city, max_per_city)
                        
                        if restaurants:
                            city_restaurants.extend(restaurants)
                            collection_message = f"Found {len(restaurants)} restaurants from {source_name} in {city}"
                        else:
                            collection_message = f"No restaurants found from {source_name} in {city}"
                            
                    except Exception as e:
                        collection_message = f"Error collecting from {source_name}: {str(e)}"
                
                time.sleep(0.5)
            
            all_restaurants.extend(city_restaurants)
            collection_progress = ((i + 1) / total_cities) * 50
        
        current_data = all_restaurants
        collection_status = "completed"
        collection_progress = 100
        collection_message = f"Data collection completed! Found {len(all_restaurants)} restaurants."
    
    def export_data(self, format_type):
        """Export data in specified format"""
        if not current_data:
            return None
        
        if format_type == 'csv':
            df = pd.DataFrame(current_data)
            # Handle social_media column
            df['social_media'] = df['social_media'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else str(x))
            # Convert all object columns to string
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            
            filename = f"restaurant_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join("web_output", filename)
            os.makedirs("web_output", exist_ok=True)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return filepath
        
        elif format_type == 'json':
            return json.dumps(current_data, indent=2, ensure_ascii=False)
        
        return None

# Initialize pipeline
pipeline = WebPipeline()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/collect', methods=['POST'])
def collect_data():
    """Start data collection"""
    global collection_status
    
    if collection_status == "collecting":
        return jsonify({"error": "Collection already in progress"})
    
    data = request.get_json()
    cities = data.get('cities', [])
    sources = data.get('sources', [])
    max_per_city = data.get('max_per_city', 20)
    
    if not cities:
        return jsonify({"error": "Please select at least one city"})
    
    if not sources:
        return jsonify({"error": "Please select at least one data source"})
    
    # Start collection in background thread
    def run_collection():
        pipeline.collect_data(cities, sources, max_per_city)
    
    thread = threading.Thread(target=run_collection)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Data collection started"})

@app.route('/api/status')
def get_status():
    """Get collection status"""
    return jsonify({
        "status": collection_status,
        "progress": collection_progress,
        "message": collection_message,
        "data_count": len(current_data)
    })

@app.route('/api/data')
def get_data():
    """Get collected data"""
    if not current_data:
        return jsonify({"error": "No data available"})
    
    return jsonify({
        "data": current_data,
        "total_count": len(current_data),
        "preview_count": len(current_data)
    })

@app.route('/api/export/<format_type>')
def export_data(format_type):
    """Export data in specified format"""
    if not current_data:
        return jsonify({"error": "No data to export"})
    
    if format_type == 'csv':
        filepath = pipeline.export_data('csv')
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({"error": "Export failed"})
    elif format_type == 'json':
        json_data = pipeline.export_data('json')
        return jsonify({"data": json_data})
    else:
        return jsonify({"error": "Unsupported format"})

@app.route('/api/summary')
def get_summary():
    """Get data summary statistics"""
    if not current_data:
        return jsonify({"error": "No data available"})
    
    df = pd.DataFrame(current_data)
    
    # Ensure proper data types for calculations
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    if 'reviews_count' in df.columns:
        df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')
    
    summary = {
        "total_restaurants": int(len(df)),
        "cities_covered": int(df['city'].nunique()) if 'city' in df.columns else 0,
        "cuisine_types": int(df['cuisine_type'].nunique()) if 'cuisine_type' in df.columns else 0,
        "data_sources": int(df['source'].nunique()) if 'source' in df.columns else 0,
        "avg_rating": float(round(df['rating'].mean(), 2)) if 'rating' in df.columns and df['rating'].notna().any() else 0.0,
        "with_phone": int((df['phone'].notna() & (df['phone'] != '')).sum()) if 'phone' in df.columns else 0,
        "with_website": int((df['website'].notna() & (df['website'] != '')).sum()) if 'website' in df.columns else 0,
        "with_social_media": int((df['social_media'].notna() & (df['social_media'] != '{}')).sum()) if 'social_media' in df.columns else 0,
        "total_reviews": int(df['reviews_count'].sum()) if 'reviews_count' in df.columns and df['reviews_count'].notna().any() else 0
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "5000"))
    print("Restaurant Lead Generation Web App")
    print("=" * 50)
    print(f"Available cities: {len(PAKISTAN_CITIES)}")
    print(f"Available cuisines: {len(CUISINE_TYPES)}")
    print("=" * 50)
    print("Starting web server...")
    print(f"Open http://localhost:{port} in your browser")

    app.run(debug=False, host="0.0.0.0", port=port)

