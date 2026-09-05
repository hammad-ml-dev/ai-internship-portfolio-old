#!/usr/bin/env python3
"""
Restaurant Lead Generation Web Application
Beautiful web interface for the restaurant lead generation pipeline
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
import sys
from datetime import datetime
import threading
import sqlite3
from contextlib import closing

# Allow importing project modules from repository root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, '.env'))
except ImportError:
    pass

# Import project modules
try:
    from config import PAKISTAN_CITIES, CUISINE_TYPES
    from main_pipeline import RestaurantLeadPipeline
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    # Fallback configuration
    PAKISTAN_CITIES = [
        'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad',
        'Multan', 'Peshawar', 'Quetta', 'Gujranwala', 'Sialkot'
    ]
    CUISINE_TYPES = [
        'Pakistani', 'BBQ', 'Chinese', 'Fast Food', 'Italian', 'Thai',
        'Indian', 'Turkish', 'Lebanese', 'Mexican', 'Japanese', 'Korean',
        'American', 'European', 'Fusion', 'Desserts', 'Beverages'
    ]

app = Flask(__name__)
CORS(app)

# Global variables
current_data = []
collection_status = "idle"
collection_progress = 0
collection_message = ""

# Database setup
DB_PATH = os.path.join(app.root_path, "data.db")

# Initialize pipeline
try:
    pipeline = RestaurantLeadPipeline()
    print("✅ Pipeline initialized successfully")
except Exception as e:
    print(f"⚠️ Pipeline initialization failed: {e}")
    pipeline = None

def init_db():
    """Initialize SQLite database"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                city TEXT,
                cuisine_type TEXT,
                phone TEXT,
                address TEXT,
                website TEXT,
                rating REAL,
                reviews_count INTEGER,
                source TEXT,
                social_media TEXT,
                description TEXT,
                lead_score REAL,
                created_at TEXT
            )
        """)
        conn.commit()

def load_from_db():
    """Load existing data from database"""
    global current_data
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            cursor = conn.execute("SELECT * FROM restaurants ORDER BY created_at DESC LIMIT 1000")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            for row in rows:
                restaurant = dict(zip(columns, row))
                if restaurant.get('social_media'):
                    try:
                        restaurant['social_media'] = json.loads(restaurant['social_media'])
                    except:
                        restaurant['social_media'] = {}
                current_data.append(restaurant)
            
            print(f"✅ Loaded {len(current_data)} records from database")
    except Exception as e:
        print(f"⚠️ Failed to load from database: {e}")

def save_to_db(restaurants):
    """Save restaurants to database"""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            for restaurant in restaurants:
                conn.execute("""
                    INSERT OR REPLACE INTO restaurants (
                        name, city, cuisine_type, phone, address, website,
                        rating, reviews_count, source, social_media, description,
                        lead_score, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    restaurant.get('name', ''),
                    restaurant.get('city', ''),
                    restaurant.get('cuisine_type', ''),
                    restaurant.get('phone', ''),
                    restaurant.get('address', ''),
                    restaurant.get('website', ''),
                    restaurant.get('rating', 0.0),
                    restaurant.get('reviews_count', 0),
                    restaurant.get('source', ''),
                    json.dumps(restaurant.get('social_media', {})),
                    restaurant.get('description', ''),
                    restaurant.get('lead_score', 0.0),
                    datetime.now().isoformat()
                ))
            conn.commit()
            print(f"✅ Saved {len(restaurants)} records to database")
    except Exception as e:
        print(f"⚠️ Failed to save to database: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/collect', methods=['POST'])
def start_collection():
    """Start data collection"""
    global collection_status, collection_progress, collection_message
    
    if not pipeline:
        return jsonify({"error": "Pipeline not available"}), 500
    
    try:
        data = request.get_json()
        cities = data.get('cities', PAKISTAN_CITIES[:3])
        sources = data.get('sources', ['demo'])
        max_per_city = data.get('max_per_city', 20)
        
        if not cities:
            return jsonify({"error": "Please select at least one city"})
        
        # Start collection in background thread
        def run_collection():
            global current_data, collection_status, collection_progress, collection_message
            
            try:
                collection_status = "running"
                collection_progress = 10
                collection_message = "Starting data collection..."
                
                # Collect data using pipeline
                all_restaurants = pipeline.collect_data(cities, max_per_city)
                
                collection_progress = 80
                collection_message = "Processing collected data..."
                
                # Update global data
                current_data = all_restaurants
                
                # Save to database
                save_to_db(all_restaurants)
                
                collection_status = "completed"
                collection_progress = 100
                collection_message = f"Collection completed! Found {len(all_restaurants)} restaurants."
                
            except Exception as e:
                collection_status = "failed"
                collection_message = f"Collection failed: {str(e)}"
                print(f"❌ Collection error: {e}")
        
        thread = threading.Thread(target=run_collection)
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "Data collection started"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to start collection: {str(e)}"}), 500

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
    return jsonify({
        "data": current_data,
        "total_count": len(current_data)
    })

@app.route('/api/export/<format_type>')
def export_data(format_type):
    """Export data in specified format"""
    if not current_data:
        return jsonify({"error": "No data to export"})
    
    try:
        if format_type == 'csv':
            # Create CSV export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"restaurant_leads_{timestamp}.csv"
            filepath = os.path.join(app.root_path, 'web_output', filename)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Export to CSV
            df = pd.DataFrame(current_data)
            df.to_csv(filepath, index=False)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        elif format_type == 'json':
            return jsonify({"data": current_data})
        else:
            return jsonify({"error": "Unsupported format"})
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/summary')
def get_summary():
    """Get data summary statistics"""
    if not current_data:
        return jsonify({"error": "No data available"})
    
    df = pd.DataFrame(current_data)
    
    summary = {
        "total_restaurants": int(len(df)),
        "cities_covered": int(df['city'].nunique()) if 'city' in df.columns else 0,
        "cuisine_types": int(df['cuisine_type'].nunique()) if 'cuisine_type' in df.columns else 0,
        "data_sources": int(df['source'].nunique()) if 'source' in df.columns else 0,
        "with_phone": int((df['phone'].notna() & (df['phone'] != '')).sum()) if 'phone' in df.columns else 0,
        "with_website": int((df['website'].notna() & (df['website'] != '')).sum()) if 'website' in df.columns else 0
    }
    
    return jsonify(summary)

@app.route('/api/cities')
def get_cities():
    """Get available cities"""
    return jsonify({"cities": PAKISTAN_CITIES})

@app.route('/api/cuisines')
def get_cuisines():
    """Get available cuisine types"""
    return jsonify({"cuisines": CUISINE_TYPES})

if __name__ == '__main__':
    print("🍕 Restaurant Lead Generation Web App")
    print("=" * 50)
    print(f"Available cities: {len(PAKISTAN_CITIES)}")
    print(f"Available cuisines: {len(CUISINE_TYPES)}")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Load existing data
    load_from_db()
    
    print("Starting web server...")
    print("Open http://localhost:5000 in your browser")
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 