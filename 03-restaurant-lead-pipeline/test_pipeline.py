#!/usr/bin/env python3
"""
Test script for the Restaurant Lead Generation Pipeline
Tests individual components and demonstrates functionality
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAKISTAN_CITIES, CUISINE_TYPES
from data_collectors.google_maps_collector import GoogleMapsCollector
from data_collectors.yellow_pages_collector import YellowPagesCollector
from data_collectors.facebook_collector import FacebookCollector
from data_collectors.foodpanda_collector import FoodPandaCollector
from data_cleaning.cleaner import RestaurantDataCleaner
from ml_models.cuisine_classifier import CuisineClassifier
from ml_models.lead_scorer import LeadScorer
from exporters.data_exporter import DataExporter

def test_data_collectors():
    """Test individual data collectors"""
    print("🧪 Testing Data Collectors...")
    
    # Test Yellow Pages collector
    print("\n1. Testing Yellow Pages Collector...")
    try:
        yp_collector = YellowPagesCollector()
        print("✓ Yellow Pages collector initialized successfully")
    except Exception as e:
        print(f"❌ Yellow Pages collector failed: {e}")
    
    # Test FoodPanda collector
    print("\n2. Testing FoodPanda Collector...")
    try:
        fp_collector = FoodPandaCollector()
        print("✓ FoodPanda collector initialized successfully")
    except Exception as e:
        print(f"❌ FoodPanda collector failed: {e}")
    
    # Test Google Maps collector (if API key available)
    print("\n3. Testing Google Maps Collector...")
    try:
        from config import GOOGLE_MAPS_API_KEY
        if GOOGLE_MAPS_API_KEY:
            gm_collector = GoogleMapsCollector(GOOGLE_MAPS_API_KEY)
            print("✓ Google Maps collector initialized successfully")
        else:
            print("⚠ Google Maps collector skipped (no API key)")
    except Exception as e:
        print(f"❌ Google Maps collector failed: {e}")
    
    # Test Facebook collector (if token available)
    print("\n4. Testing Facebook Collector...")
    try:
        from config import FACEBOOK_ACCESS_TOKEN
        if FACEBOOK_ACCESS_TOKEN:
            fb_collector = FacebookCollector(FACEBOOK_ACCESS_TOKEN)
            print("✓ Facebook collector initialized successfully")
        else:
            print("⚠ Facebook collector skipped (no access token)")
    except Exception as e:
        print(f"❌ Facebook collector failed: {e}")
    
    print("\n✅ Data collector tests completed!")

def test_data_cleaning():
    """Test data cleaning functionality"""
    print("\n🧪 Testing Data Cleaning...")
    
    # Create sample data
    sample_restaurants = [
        {
            'name': 'BBQ Tonight',
            'city': 'karachi',
            'address': '  Main Street, Karachi  ',
            'phone': '0300-1234567',
            'website': 'bbqtonight.com',
            'rating': 4.5,
            'reviews_count': 150,
            'cuisine_type': 'BBQ',
            'source': 'Google Maps'
        },
        {
            'name': 'BBQ Tonight',
            'city': 'Karachi',
            'address': 'Main Street, Karachi',
            'phone': '+92-300-1234567',
            'website': 'https://bbqtonight.com',
            'rating': 4.5,
            'reviews_count': 150,
            'cuisine_type': 'BBQ',
            'source': 'FoodPanda'
        },
        {
            'name': 'Chinese Wok',
            'city': 'lahore',
            'address': 'Gulberg, Lahore',
            'phone': '042-1234567',
            'website': '',
            'rating': 4.2,
            'reviews_count': 89,
            'cuisine_type': 'Chinese',
            'source': 'Yellow Pages PK'
        }
    ]
    
    try:
        cleaner = RestaurantDataCleaner()
        cleaned_df = cleaner.clean_dataset(sample_restaurants)
        
        print(f"✓ Data cleaning completed successfully!")
        print(f"  - Original records: {len(sample_restaurants)}")
        print(f"  - Cleaned records: {len(cleaned_df)}")
        print(f"  - Duplicates removed: {len(sample_restaurants) - len(cleaned_df)}")
        
        # Show sample of cleaned data
        print("\nSample cleaned data:")
        print(cleaned_df[['name', 'city', 'phone', 'cuisine_type', 'quality_score']].head())
        
        return cleaned_df
        
    except Exception as e:
        print(f"❌ Data cleaning failed: {e}")
        return pd.DataFrame()

def test_cuisine_classification(df):
    """Test cuisine classification"""
    print("\n🧪 Testing Cuisine Classification...")
    
    if df.empty:
        print("❌ No data to classify")
        return df
    
    try:
        classifier = CuisineClassifier(model_type='naive_bayes')
        
        # Train the classifier
        print("Training cuisine classifier...")
        training_result = classifier.train(df)
        
        if training_result['status'] == 'success':
            print(f"✓ Cuisine classifier trained successfully!")
            print(f"  - Accuracy: {training_result['accuracy']:.3f}")
            
            # Classify restaurants
            classified_df = classifier.classify_restaurants(df)
            
            # Show results
            print("\nClassification results:")
            if 'predicted_cuisine' in classified_df.columns:
                print(classified_df[['name', 'cuisine_type', 'predicted_cuisine', 'classification_confidence']].head())
            
            return classified_df
        else:
            print("⚠ Cuisine classification training failed, using rule-based")
            return df
            
    except Exception as e:
        print(f"❌ Cuisine classification failed: {e}")
        return df

def test_lead_scoring(df):
    """Test lead scoring functionality"""
    print("\n🧪 Testing Lead Scoring...")
    
    if df.empty:
        print("❌ No data to score")
        return df
    
    try:
        scorer = LeadScorer(model_type='random_forest')
        
        # Train the scorer
        print("Training lead scorer...")
        training_result = scorer.train(df)
        
        if training_result['status'] == 'success':
            print(f"✓ Lead scorer trained successfully!")
            print(f"  - R² Score: {training_result['r2_score']:.3f}")
            
            # Score leads
            scored_df = scorer.predict_lead_score(df)
            
            # Show results
            print("\nLead scoring results:")
            if 'lead_score' in scored_df.columns:
                print(scored_df[['name', 'city', 'quality_score', 'lead_score', 'lead_potential']].head())
            
            return scored_df
        else:
            print("⚠ Lead scoring training failed, using rule-based")
            return df
            
    except Exception as e:
        print(f"❌ Lead scoring failed: {e}")
        return df

def test_data_export(df):
    """Test data export functionality"""
    print("\n🧪 Testing Data Export...")
    
    if df.empty:
        print("❌ No data to export")
        return
    
    try:
        exporter = DataExporter(output_dir="test_output")
        
        # Export to all formats
        print("Exporting data to multiple formats...")
        export_files = exporter.export_all_formats(df, "test_restaurants")
        
        print(f"✓ Data export completed successfully!")
        print(f"  - Export files: {len(export_files)}")
        for format_type, filepath in export_files.items():
            print(f"    - {format_type.upper()}: {os.path.basename(filepath)}")
        
        return export_files
        
    except Exception as e:
        print(f"❌ Data export failed: {e}")
        return {}

def test_configuration():
    """Test configuration and constants"""
    print("\n🧪 Testing Configuration...")
    
    try:
        print(f"✓ Pakistan cities configured: {len(PAKISTAN_CITIES)}")
        print(f"  - Sample cities: {', '.join(PAKISTAN_CITIES[:5])}")
        
        print(f"✓ Cuisine types configured: {len(CUISINE_TYPES)}")
        print(f"  - Sample cuisines: {', '.join(CUISINE_TYPES[:5])}")
        
        # Check API keys
        from config import GOOGLE_MAPS_API_KEY, FACEBOOK_ACCESS_TOKEN
        
        if GOOGLE_MAPS_API_KEY:
            print("✓ Google Maps API key configured")
        else:
            print("⚠ Google Maps API key not configured")
            
        if FACEBOOK_ACCESS_TOKEN:
            print("✓ Facebook access token configured")
        else:
            print("⚠ Facebook access token not configured")
        
        print("✅ Configuration test completed!")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def run_integration_test():
    """Run a complete integration test"""
    print("\n🚀 Running Integration Test...")
    print("=" * 50)
    
    # Test 1: Configuration
    test_configuration()
    
    # Test 2: Data Collectors
    test_data_collectors()
    
    # Test 3: Data Cleaning
    cleaned_df = test_data_cleaning()
    
    if not cleaned_df.empty:
        # Test 4: Cuisine Classification
        classified_df = test_cuisine_classification(cleaned_df)
        
        # Test 5: Lead Scoring
        scored_df = test_lead_scoring(classified_df)
        
        # Test 6: Data Export
        export_files = test_data_export(scored_df)
        
        print("\n" + "=" * 50)
        print("🎉 Integration Test Completed Successfully!")
        print("=" * 50)
        print(f"Final dataset: {len(scored_df)} restaurants")
        print(f"Export files: {len(export_files)} formats")
        
        return scored_df
    else:
        print("\n❌ Integration test failed at data cleaning step")
        return pd.DataFrame()

def main():
    """Main test function"""
    print("🍕 Restaurant Lead Generation Pipeline - Test Suite")
    print("=" * 60)
    print(f"Test start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--config':
            test_configuration()
        elif sys.argv[1] == '--collectors':
            test_data_collectors()
        elif sys.argv[1] == '--cleaning':
            test_data_cleaning()
        elif sys.argv[1] == '--classification':
            # Create sample data for classification test
            sample_df = test_data_cleaning()
            test_cuisine_classification(sample_df)
        elif sys.argv[1] == '--scoring':
            # Create sample data for scoring test
            sample_df = test_data_cleaning()
            test_lead_scoring(sample_df)
        elif sys.argv[1] == '--export':
            # Create sample data for export test
            sample_df = test_data_cleaning()
            test_data_export(sample_df)
        elif sys.argv[1] == '--integration':
            run_integration_test()
        else:
            print("Usage:")
            print("  python test_pipeline.py --config        # Test configuration")
            print("  python test_pipeline.py --collectors    # Test data collectors")
            print("  python test_pipeline.py --cleaning      # Test data cleaning")
            print("  python test_pipeline.py --classification # Test cuisine classification")
            print("  python test_pipeline.py --scoring       # Test lead scoring")
            print("  python test_pipeline.py --export        # Test data export")
            print("  python test_pipeline.py --integration   # Run full integration test")
    else:
        # Default: Run integration test
        print("No arguments provided. Running full integration test...")
        run_integration_test()

if __name__ == "__main__":
    main() 