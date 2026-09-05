#!/usr/bin/env python3
"""
Pakistan Restaurant Lead Generation Pipeline
Main script to orchestrate the entire process
Enhanced with comprehensive error handling and robustness
"""

import os
import sys
import time
import logging
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import traceback

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import with error handling
try:
    from config import PAKISTAN_CITIES, GOOGLE_MAPS_API_KEY, FACEBOOK_ACCESS_TOKEN
except ImportError as e:
    logger.error(f"Failed to import config: {e}")
    # Fallback configuration
    PAKISTAN_CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad']
    GOOGLE_MAPS_API_KEY = None
    FACEBOOK_ACCESS_TOKEN = None

try:
    from data_collectors.enhanced_collector import EnhancedCollector
    from data_collectors.demo_collector import DemoCollector
    from data_collectors.google_maps_collector import GoogleMapsCollector
    from data_collectors.yellow_pages_collector import YellowPagesCollector
    from data_collectors.facebook_collector import FacebookCollector
    from data_collectors.foodpanda_collector import FoodPandaCollector
    from data_cleaning.cleaner import RestaurantDataCleaner
    from ml_models.cuisine_classifier import CuisineClassifier
    from ml_models.lead_scorer import LeadScorer
    from exporters.data_exporter import DataExporter
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    # Create fallback classes
    class FallbackCollector:
        def search_restaurants(self, city, max_per_city):
            return [{'name': f'Demo Restaurant in {city}', 'city': city, 'source': 'fallback'}]
    
    EnhancedCollector = FallbackCollector
    DemoCollector = FallbackCollector
    GoogleMapsCollector = FallbackCollector
    YellowPagesCollector = FallbackCollector
    FacebookCollector = FallbackCollector
    FoodPandaCollector = FallbackCollector
    RestaurantDataCleaner = None
    CuisineClassifier = None
    LeadScorer = None
    DataExporter = None

class RestaurantLeadPipeline:
    def __init__(self):
        """Initialize the pipeline with comprehensive error handling"""
        try:
            self._setup_directories()
            self._initialize_components()
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            self._setup_fallback_components()
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = ['models', 'output', 'logs', 'temp']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
    
    def _initialize_components(self):
        """Initialize all pipeline components with error handling"""
        self.collectors = {}
        self.all_restaurants = []
        
        # Initialize enhanced collector
        try:
            self.enhanced_collector = EnhancedCollector(max_workers=4)  # Reduced for stability
            logger.info("Enhanced collector initialized")
        except Exception as e:
            logger.warning(f"Enhanced collector failed: {e}")
            self.enhanced_collector = None
        
        # Initialize data cleaner
        try:
            self.cleaner = RestaurantDataCleaner() if RestaurantDataCleaner else None
            logger.info("Data cleaner initialized")
        except Exception as e:
            logger.warning(f"Data cleaner failed: {e}")
            self.cleaner = None
        
        # Initialize ML models
        try:
            self.cuisine_classifier = CuisineClassifier() if CuisineClassifier else None
            self.lead_scorer = LeadScorer() if LeadScorer else None
            logger.info("ML models initialized")
        except Exception as e:
            logger.warning(f"ML models failed: {e}")
            self.cuisine_classifier = None
            self.lead_scorer = None
        
        # Initialize data exporter
        try:
            self.exporter = DataExporter() if DataExporter else None
            logger.info("Data exporter initialized")
        except Exception as e:
            logger.warning(f"Data exporter failed: {e}")
            self.exporter = None
        
        # Initialize data collectors
        self._initialize_collectors()
    
    def _setup_fallback_components(self):
        """Setup fallback components when main components fail"""
        logger.info("Setting up fallback components...")
        
        class SimpleCollector:
            def search_restaurants(self, city, max_per_city):
                return [{'name': f'Fallback Restaurant in {city}', 'city': city, 'source': 'fallback'}]
        
        self.collectors = {'fallback': SimpleCollector()}
        self.enhanced_collector = None
        self.cleaner = None
        self.cuisine_classifier = None
        self.lead_scorer = None
        self.exporter = None
        self.all_restaurants = []
    
    def _initialize_collectors(self):
        """Initialize all data collectors with comprehensive error handling"""
        logger.info("Initializing data collectors...")
        
        # Google Maps collector (requires API key)
        if GOOGLE_MAPS_API_KEY:
            try:
                self.collectors['google_maps'] = GoogleMapsCollector(GOOGLE_MAPS_API_KEY)
                logger.info("✓ Google Maps collector initialized")
            except Exception as e:
                logger.warning(f"⚠ Google Maps collector failed: {e}")
        else:
            logger.info("⚠ Google Maps collector not initialized (API key missing)")
        
        # Yellow Pages collector
        try:
            self.collectors['yellow_pages'] = YellowPagesCollector()
            logger.info("✓ Yellow Pages collector initialized")
        except Exception as e:
            logger.warning(f"⚠ Yellow Pages collector failed: {e}")
        
        # Facebook collector
        if FACEBOOK_ACCESS_TOKEN:
            try:
                self.collectors['facebook'] = FacebookCollector(FACEBOOK_ACCESS_TOKEN)
                logger.info("✓ Facebook collector initialized")
            except Exception as e:
                logger.warning(f"⚠ Facebook collector failed: {e}")
        else:
            logger.info("⚠ Facebook collector not initialized (access token missing)")
        
        # FoodPanda collector
        try:
            self.collectors['foodpanda'] = FoodPandaCollector()
            logger.info("✓ FoodPanda collector initialized")
        except Exception as e:
            logger.warning(f"⚠ FoodPanda collector failed: {e}")
        
        # Demo collector (always available for testing)
        try:
            self.collectors['demo'] = DemoCollector("Main Pipeline Demo")
            logger.info("✓ Demo collector initialized")
        except Exception as e:
            logger.warning(f"⚠ Demo collector failed: {e}")
        
        # Ensure at least one collector is available
        if not self.collectors:
            logger.error("No collectors available, creating emergency fallback")
            self._setup_fallback_components()
        
        logger.info(f"Total collectors initialized: {len(self.collectors)}")
    
    def collect_data(self, cities: List[str] = None, max_per_city: int = 100) -> List[Dict]:
        """Collect restaurant data from all sources with enhanced error handling"""
        if cities is None:
            cities = PAKISTAN_CITIES[:5]  # Start with top 5 cities for stability
        
        logger.info(f"🚀 Starting data collection for {len(cities)} cities...")
        logger.info(f"Cities: {', '.join(cities)}")
        
        all_restaurants = []
        
        for city in cities:
            logger.info(f"📍 Collecting data for {city}...")
            city_restaurants = []
            
            # Collect from each source with error handling
            for source_name, collector in self.collectors.items():
                try:
                    logger.info(f"  🔍 Searching {source_name}...")
                    restaurants = collector.search_restaurants(city, max_per_city)
                    
                    if restaurants:
                        logger.info(f"    ✓ Found {len(restaurants)} restaurants")
                        city_restaurants.extend(restaurants)
                    else:
                        logger.info(f"    ⚠ No restaurants found")
                        
                except Exception as e:
                    logger.error(f"    ❌ Error collecting from {source_name}: {str(e)}")
                    continue
            
            # Remove duplicates within city
            city_restaurants = self._remove_city_duplicates(city_restaurants)
            logger.info(f"  📊 Total unique restaurants in {city}: {len(city_restaurants)}")
            
            all_restaurants.extend(city_restaurants)
            
            # Add delay between cities
            time.sleep(1)
        
        logger.info(f"🎯 Data collection completed!")
        logger.info(f"Total restaurants collected: {len(all_restaurants)}")
        
        self.all_restaurants = all_restaurants
        return all_restaurants
    
    def collect_large_dataset(self, target_total: int = 5000, cities: List[str] = None) -> List[Dict]:
        """Collect large dataset using enhanced collector for 5k+ leads"""
        logger.info(f"🚀 Starting LARGE SCALE data collection...")
        logger.info(f"🎯 Target: {target_total:,} restaurants")
        
        try:
            if self.enhanced_collector:
                # Use enhanced collector for large datasets
                restaurants = self.enhanced_collector.collect_large_dataset(cities, target_total)
                
                logger.info(f"✅ Large scale collection completed!")
                logger.info(f"📊 Total restaurants: {len(restaurants):,}")
                
                self.all_restaurants = restaurants
                return restaurants
            else:
                logger.warning("Enhanced collector not available, using standard collection")
                return self.collect_data(cities, 200)
            
        except Exception as e:
            logger.error(f"❌ Large scale collection failed: {str(e)}")
            logger.info("🔄 Falling back to standard collection...")
            return self.collect_data(cities, 100)
    
    def _remove_city_duplicates(self, restaurants: List[Dict]) -> List[Dict]:
        """Remove duplicate restaurants within a city"""
        if not restaurants:
            return restaurants
        
        # Create a set of unique identifiers (name + city)
        seen = set()
        unique_restaurants = []
        
        for restaurant in restaurants:
            identifier = f"{restaurant.get('name', '').lower()}_{restaurant.get('city', '').lower()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_restaurants.append(restaurant)
        
        return unique_restaurants
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and prepare the collected data with fallback"""
        logger.info("🧹 Starting data cleaning process...")
        
        if not self.all_restaurants:
            logger.error("❌ No data to clean. Run collect_data() first.")
            return pd.DataFrame()
        
        try:
            if self.cleaner:
                # Clean the data using the cleaner
                cleaned_df = self.cleaner.clean_dataset(self.all_restaurants)
                logger.info(f"✓ Data cleaning completed!")
                logger.info(f"  - Original records: {len(self.all_restaurants)}")
                logger.info(f"  - Cleaned records: {len(cleaned_df)}")
                logger.info(f"  - Duplicates removed: {len(self.all_restaurants) - len(cleaned_df)}")
            else:
                # Fallback cleaning
                logger.warning("Data cleaner not available, using fallback cleaning")
                cleaned_df = self._fallback_cleaning()
            
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            logger.info("Using fallback cleaning...")
            return self._fallback_cleaning()
    
    def _fallback_cleaning(self) -> pd.DataFrame:
        """Fallback data cleaning when main cleaner fails"""
        logger.info("Using fallback data cleaning...")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.all_restaurants)
        
        if df.empty:
            return df
        
        # Basic cleaning
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        logger.info(f"Fallback cleaning completed: {len(df)} records")
        return df
    
    def classify_cuisines(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify restaurants by cuisine type using ML with fallback"""
        logger.info("🍽️ Starting cuisine classification...")
        
        if df.empty:
            logger.error("❌ No data to classify.")
            return df
        
        try:
            if self.cuisine_classifier:
                # Train the cuisine classifier
                logger.info("Training cuisine classifier...")
                training_result = self.cuisine_classifier.train(df)
                
                if training_result.get('status') == 'success':
                    logger.info(f"✓ Cuisine classifier trained successfully (Accuracy: {training_result.get('accuracy', 0):.3f})")
                    
                    # Classify restaurants
                    classified_df = self.cuisine_classifier.classify_restaurants(df)
                    
                    # Save the trained model
                    try:
                        os.makedirs('models', exist_ok=True)
                        self.cuisine_classifier.save_model('models/cuisine_classifier.pkl')
                    except Exception as e:
                        logger.warning(f"Failed to save model: {e}")
                    
                    return classified_df
                else:
                    logger.warning("⚠ Cuisine classification training failed, using rule-based classification")
                    return self._rule_based_cuisine_classification(df)
            else:
                logger.warning("Cuisine classifier not available, using rule-based classification")
                return self._rule_based_cuisine_classification(df)
                
        except Exception as e:
            logger.error(f"Cuisine classification failed: {e}")
            logger.info("Using rule-based classification...")
            return self._rule_based_cuisine_classification(df)
    
    def _rule_based_cuisine_classification(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rule-based cuisine classification when ML fails"""
        logger.info("Using rule-based cuisine classification...")
        
        if 'cuisine_type' not in df.columns:
            df['cuisine_type'] = 'Pakistani'  # Default cuisine
        
        # Simple keyword-based classification
        cuisine_keywords = {
            'Pakistani': ['pakistani', 'desi', 'local', 'traditional'],
            'Chinese': ['chinese', 'mandarin', 'cantonese', 'szechuan'],
            'Fast Food': ['fast food', 'burger', 'pizza', 'fries'],
            'BBQ': ['bbq', 'barbecue', 'grill', 'smoke'],
            'Italian': ['italian', 'pasta', 'pizza', 'risotto'],
            'Thai': ['thai', 'pad thai', 'curry', 'lemongrass']
        }
        
        for cuisine, keywords in cuisine_keywords.items():
            mask = df['name'].str.contains('|'.join(keywords), case=False, na=False)
            df.loc[mask, 'cuisine_type'] = cuisine
        
        logger.info("Rule-based classification completed")
        return df
    
    def score_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Score restaurant leads for potential with fallback"""
        logger.info("📊 Starting lead scoring...")
        
        if df.empty:
            logger.error("❌ No data to score.")
            return df
        
        try:
            if self.lead_scorer:
                # Train the lead scorer
                logger.info("Training lead scorer...")
                training_result = self.lead_scorer.train(df)
                
                if training_result.get('status') == 'success':
                    logger.info(f"✓ Lead scorer trained successfully (R²: {training_result.get('r2_score', 0):.3f})")
                    
                    # Score leads
                    scored_df = self.lead_scorer.predict_lead_score(df)
                    
                    # Save the trained model
                    try:
                        os.makedirs('models', exist_ok=True)
                        self.lead_scorer.save_model('models/lead_scorer.pkl')
                    except Exception as e:
                        logger.warning(f"Failed to save model: {e}")
                    
                    return scored_df
                else:
                    logger.warning("⚠ Lead scoring training failed, using rule-based scoring")
                    return self._rule_based_lead_scoring(df)
            else:
                logger.warning("Lead scorer not available, using rule-based scoring")
                return self._rule_based_lead_scoring(df)
                
        except Exception as e:
            logger.error(f"Lead scoring failed: {e}")
            logger.info("Using rule-based scoring...")
            return self._rule_based_lead_scoring(df)
    
    def _rule_based_lead_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rule-based lead scoring when ML fails"""
        logger.info("Using rule-based lead scoring...")
        
        if 'lead_score' not in df.columns:
            df['lead_score'] = 50  # Default score
        
        # Simple scoring based on available data
        for idx, row in df.iterrows():
            score = 50  # Base score
            
            # Increase score for complete data
            if pd.notna(row.get('phone')) and str(row['phone']).strip():
                score += 10
            if pd.notna(row.get('address')) and str(row['address']).strip():
                score += 10
            if pd.notna(row.get('rating')) and float(row['rating']) > 0:
                score += 15
            if pd.notna(row.get('website')) and str(row['website']).strip():
                score += 15
            
            df.at[idx, 'lead_score'] = min(100, score)
        
        logger.info("Rule-based lead scoring completed")
        return df
    
    def export_data(self, df: pd.DataFrame) -> Dict[str, str]:
        """Export the processed data to multiple formats with fallback"""
        logger.info("📤 Starting data export...")
        
        if df.empty:
            logger.error("❌ No data to export.")
            return {}
        
        try:
            if self.exporter:
                # Export to all formats using the exporter
                export_files = self.exporter.export_all_formats(df)
                logger.info("✓ Data export completed!")
                return export_files
            else:
                # Fallback export
                logger.warning("Data exporter not available, using fallback export")
                return self._fallback_export(df)
                
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            logger.info("Using fallback export...")
            return self._fallback_export(df)
    
    def _fallback_export(self, df: pd.DataFrame) -> Dict[str, str]:
        """Fallback data export when main exporter fails"""
        logger.info("Using fallback data export...")
        
        os.makedirs('output', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_files = {}
        
        try:
            # Export to CSV
            csv_file = f"output/restaurant_leads_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            export_files['csv'] = csv_file
            logger.info(f"CSV exported: {csv_file}")
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
        
        try:
            # Export to Excel
            excel_file = f"output/restaurant_leads_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            export_files['excel'] = excel_file
            logger.info(f"Excel exported: {excel_file}")
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
        
        return export_files
    
    def run_full_pipeline(self, cities: List[str] = None, max_per_city: int = 50, large_scale: bool = False) -> pd.DataFrame:
        """Run the complete pipeline from data collection to export with comprehensive error handling"""
        logger.info("=" * 60)
        logger.info("🍕 PAKISTAN RESTAURANT LEAD GENERATION PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Data Collection
            if large_scale:
                self.collect_large_dataset(5000, cities)
            else:
                self.collect_data(cities, max_per_city)
            
            # Step 2: Data Cleaning
            cleaned_df = self.clean_data()
            
            if cleaned_df.empty:
                logger.error("❌ Pipeline failed: No data after cleaning")
                return cleaned_df
            
            # Step 3: Cuisine Classification (Optional ML)
            classified_df = self.classify_cuisines(cleaned_df)
            
            # Step 4: Lead Scoring (Optional ML)
            scored_df = self.score_leads(classified_df)
            
            # Step 5: Data Export
            export_files = self.export_data(scored_df)
            
            # Final summary
            logger.info("\n" + "=" * 60)
            logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Final dataset: {len(scored_df)} restaurants")
            logger.info(f"Export files: {len(export_files)} formats")
            logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return scored_df
            
        except Exception as e:
            logger.error(f"\n❌ Pipeline failed with error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()
    
    def run_quick_test(self) -> pd.DataFrame:
        """Run a quick test with limited cities and data"""
        logger.info("🧪 Running quick test pipeline...")
        
        test_cities = ['Karachi', 'Lahore']  # Test with 2 major cities
        max_per_city = 20  # Limited data per city
        
        return self.run_full_pipeline(test_cities, max_per_city)
    
    def run_large_scale_pipeline(self, cities: List[str] = None) -> pd.DataFrame:
        """Run large-scale pipeline for 5k+ leads"""
        logger.info("🚀 Running LARGE SCALE pipeline for 5k+ leads...")
        
        if cities is None:
            cities = PAKISTAN_CITIES[:15]  # Use more cities for large scale
        
        return self.run_full_pipeline(cities, 300, large_scale=True)
    
    def health_check(self) -> Dict[str, bool]:
        """Check the health of all pipeline components"""
        health_status = {
            'enhanced_collector': self.enhanced_collector is not None,
            'data_cleaner': self.cleaner is not None,
            'cuisine_classifier': self.cuisine_classifier is not None,
            'lead_scorer': self.lead_scorer is not None,
            'data_exporter': self.exporter is not None,
            'data_collectors': len(self.collectors) > 0
        }
        
        logger.info("Pipeline Health Check:")
        for component, status in health_status.items():
            status_symbol = "✓" if status else "❌"
            logger.info(f"  {status_symbol} {component}: {'OK' if status else 'FAILED'}")
        
        return health_status

def main():
    """Main function to run the pipeline with comprehensive error handling"""
    try:
        pipeline = RestaurantLeadPipeline()
        
        # Run health check
        health_status = pipeline.health_check()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                # Run quick test
                pipeline.run_quick_test()
            elif sys.argv[1] == '--full':
                # Run full pipeline
                pipeline.run_full_pipeline()
            elif sys.argv[1] == '--large':
                # Run large-scale pipeline for 5k+ leads
                pipeline.run_large_scale_pipeline()
            elif sys.argv[1] == '--cities':
                # Run with specific cities
                cities = sys.argv[2].split(',')
                pipeline.run_full_pipeline(cities)
            elif sys.argv[1] == '--health':
                # Run health check only
                pipeline.health_check()
            else:
                print("Usage:")
                print("  python main_pipeline.py --test     # Run quick test")
                print("  python main_pipeline.py --full     # Run full pipeline")
                print("  python main_pipeline.py --large    # Run large-scale pipeline (5k+ leads)")
                print("  python main_pipeline.py --cities Karachi,Lahore  # Run with specific cities")
                print("  python main_pipeline.py --health   # Check pipeline health")
        else:
            # Default: Run quick test
            print("No arguments provided. Running quick test...")
            pipeline.run_quick_test()
            
    except Exception as e:
        logger.error(f"Main function failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Pipeline failed to start: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    main() 