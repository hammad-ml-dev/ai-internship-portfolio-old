#!/usr/bin/env python3
"""
Robust Restaurant Lead Generation Pipeline
Enhanced with comprehensive error handling and fallbacks
"""

import os
import sys
import time
import logging
from typing import List, Dict
import pandas as pd
from datetime import datetime
import traceback

# Setup logging with ASCII-safe characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs('models', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('logs', exist_ok=True)

class RobustRestaurantPipeline:
    def __init__(self):
        """Initialize the robust pipeline"""
        self.restaurants = []
        self._setup_collectors()
        
    def _setup_collectors(self):
        """Setup data collectors with fallbacks"""
        self.collectors = {}
        
        # Always available demo collector
        try:
            from data_collectors.demo_collector import DemoCollector
            self.collectors['demo'] = DemoCollector("Robust Pipeline")
            logger.info("Demo collector initialized")
        except Exception as e:
            logger.warning(f"Demo collector failed: {e}")
            self._create_fallback_collector()
    
    def _create_fallback_collector(self):
        """Create a fallback collector when others fail"""
        class FallbackCollector:
            def __init__(self, name):
                self.name = name
            
            def search_restaurants(self, city, max_per_city):
                return [
                    {
                        'name': f'Fallback Restaurant in {city}',
                        'city': city,
                        'phone': '+92-300-1234567',
                        'address': f'Main Street, {city}',
                        'rating': 4.0,
                        'cuisine_type': 'Pakistani',
                        'source': 'fallback'
                    }
                ]
        
        self.collectors['fallback'] = FallbackCollector("Emergency Fallback")
        logger.info("Fallback collector created")
    
    def collect_data(self, cities: List[str] = None, max_per_city: int = 50) -> List[Dict]:
        """Collect restaurant data with error handling"""
        if cities is None:
            cities = ['Karachi', 'Lahore', 'Islamabad']
        
        logger.info(f"Starting data collection for {len(cities)} cities...")
        
        all_restaurants = []
        
        for city in cities:
            logger.info(f"Collecting data for {city}...")
            
            for source_name, collector in self.collectors.items():
                try:
                    restaurants = collector.search_restaurants(city, max_per_city)
                    if restaurants:
                        all_restaurants.extend(restaurants)
                        logger.info(f"  {source_name}: {len(restaurants)} restaurants")
                except Exception as e:
                    logger.error(f"  {source_name} failed: {e}")
                    continue
            
            time.sleep(1)  # Delay between cities
        
        # Remove duplicates
        unique_restaurants = self._remove_duplicates(all_restaurants)
        logger.info(f"Total unique restaurants: {len(unique_restaurants)}")
        
        self.restaurants = unique_restaurants
        return unique_restaurants
    
    def _remove_duplicates(self, restaurants: List[Dict]) -> List[Dict]:
        """Remove duplicate restaurants"""
        if not restaurants:
            return restaurants
        
        seen = set()
        unique = []
        
        for restaurant in restaurants:
            identifier = f"{restaurant.get('name', '')}_{restaurant.get('city', '')}"
            if identifier not in seen:
                seen.add(identifier)
                unique.append(restaurant)
        
        return unique
    
    def clean_data(self) -> pd.DataFrame:
        """Clean the collected data"""
        logger.info("Cleaning data...")
        
        if not self.restaurants:
            logger.error("No data to clean")
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(self.restaurants)
            
            # Basic cleaning
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Add quality score
            df['quality_score'] = 50  # Base score
            
            # Increase score for complete data
            for idx, row in df.iterrows():
                score = 50
                if pd.notna(row.get('phone')) and str(row['phone']).strip():
                    score += 10
                if pd.notna(row.get('address')) and str(row['address']).strip():
                    score += 10
                if pd.notna(row.get('rating')) and float(row['rating']) > 0:
                    score += 15
                df.at[idx, 'quality_score'] = min(100, score)
            
            logger.info(f"Data cleaning completed: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            return pd.DataFrame()
    
    def export_data(self, df: pd.DataFrame) -> Dict[str, str]:
        """Export data to multiple formats"""
        logger.info("Exporting data...")
        
        if df.empty:
            logger.error("No data to export")
            return {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_files = {}
        
        try:
            # CSV export
            csv_file = f"output/restaurant_leads_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            export_files['csv'] = csv_file
            logger.info(f"CSV exported: {csv_file}")
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
        
        try:
            # Excel export
            excel_file = f"output/restaurant_leads_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            export_files['excel'] = excel_file
            logger.info(f"Excel exported: {excel_file}")
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
        
        return export_files
    
    def run_pipeline(self, cities: List[str] = None, max_per_city: int = 50) -> pd.DataFrame:
        """Run the complete pipeline"""
        logger.info("=" * 50)
        logger.info("RESTAURANT LEAD GENERATION PIPELINE")
        logger.info("=" * 50)
        
        try:
            # Step 1: Data Collection
            self.collect_data(cities, max_per_city)
            
            # Step 2: Data Cleaning
            cleaned_df = self.clean_data()
            
            if cleaned_df.empty:
                logger.error("Pipeline failed: No data after cleaning")
                return cleaned_df
            
            # Step 3: Data Export
            export_files = self.export_data(cleaned_df)
            
            logger.info("=" * 50)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"Final dataset: {len(cleaned_df)} restaurants")
            logger.info(f"Export files: {len(export_files)} formats")
            logger.info("=" * 50)
            
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def run_test(self) -> pd.DataFrame:
        """Run a quick test"""
        logger.info("Running quick test...")
        return self.run_pipeline(['Karachi', 'Lahore'], 20)

def main():
    """Main function"""
    try:
        pipeline = RobustRestaurantPipeline()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                pipeline.run_test()
            elif sys.argv[1] == '--full':
                pipeline.run_pipeline()
            elif sys.argv[1] == '--cities':
                cities = sys.argv[2].split(',')
                pipeline.run_pipeline(cities)
            else:
                print("Usage:")
                print("  python robust_pipeline.py --test")
                print("  python robust_pipeline.py --full")
                print("  python robust_pipeline.py --cities Karachi,Lahore")
        else:
            print("Running test pipeline...")
            pipeline.run_test()
            
    except Exception as e:
        logger.error(f"Main function failed: {e}")
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
