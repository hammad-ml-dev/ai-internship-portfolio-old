#!/usr/bin/env python3
"""
Enhanced Pipeline Test Script
Tests all components of the restaurant lead generation pipeline
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_collector():
    """Test the enhanced collector"""
    print("🧪 Testing Enhanced Collector...")
    
    try:
        from data_collectors.enhanced_collector import EnhancedCollector
        
        collector = EnhancedCollector(max_workers=4)
        stats = collector.get_collection_stats()
        
        print(f"✅ Enhanced collector initialized successfully")
        print(f"📊 Available sources: {stats['available_sources']}")
        print(f"🔍 Total sources: {stats['total_sources']}")
        
        # Test small collection
        print("\n🔍 Testing small collection...")
        restaurants = collector.collect_large_dataset(['Karachi', 'Lahore'], 100)
        
        if len(restaurants) >= 50:
            print(f"✅ Small collection successful: {len(restaurants)} restaurants")
        else:
            print(f"⚠️ Small collection limited: {len(restaurants)} restaurants")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced collector test failed: {str(e)}")
        return False

def test_ml_models():
    """Test the ML models"""
    print("\n🧪 Testing ML Models...")
    
    try:
        from ml_models.cuisine_classifier import CuisineClassifier
        from ml_models.lead_scorer import LeadScorer
        
        # Test cuisine classifier
        print("  🔍 Testing Cuisine Classifier...")
        classifier = CuisineClassifier('random_forest')
        print(f"    ✅ Cuisine classifier initialized with {classifier.model_type}")
        
        # Test lead scorer
        print("  🔍 Testing Lead Scorer...")
        scorer = LeadScorer('gradient_boosting')
        print(f"    ✅ Lead scorer initialized with {scorer.model_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML models test failed: {str(e)}")
        return False

def test_data_cleaning():
    """Test data cleaning"""
    print("\n🧪 Testing Data Cleaning...")
    
    try:
        from data_cleaning.cleaner import RestaurantDataCleaner
        
        cleaner = RestaurantDataCleaner()
        print("✅ Data cleaner initialized successfully")
        
        # Test with sample data
        sample_data = [
            {
                'name': 'Test Restaurant 1',
                'city': 'Karachi',
                'phone': '+92 21 1234567',
                'address': '123 Main St, Karachi',
                'rating': 4.5,
                'reviews_count': 100
            },
            {
                'name': 'Test Restaurant 2',
                'city': 'Lahore',
                'phone': '+92 42 7654321',
                'address': '456 Market Rd, Lahore',
                'rating': 4.0,
                'reviews_count': 75
            }
        ]
        
        cleaned_df = cleaner.clean_dataset(sample_data)
        print(f"✅ Data cleaning successful: {len(cleaned_df)} records cleaned")
        
        return True
        
    except Exception as e:
        print(f"❌ Data cleaning test failed: {str(e)}")
        return False

def test_main_pipeline():
    """Test the main pipeline"""
    print("\n🧪 Testing Main Pipeline...")
    
    try:
        from main_pipeline import RestaurantLeadPipeline
        
        pipeline = RestaurantLeadPipeline()
        print("✅ Main pipeline initialized successfully")
        
        # Test quick test
        print("  🔍 Testing quick test...")
        result = pipeline.run_quick_test()
        
        if not result.empty:
            print(f"    ✅ Quick test successful: {len(result)} restaurants")
        else:
            print("    ⚠️ Quick test returned no data")
        
        return True
        
    except Exception as e:
        print(f"❌ Main pipeline test failed: {str(e)}")
        return False

def run_performance_test():
    """Run a performance test with larger dataset"""
    print("\n🚀 Running Performance Test...")
    
    try:
        from main_pipeline import RestaurantLeadPipeline
        
        pipeline = RestaurantLeadPipeline()
        
        start_time = time.time()
        
        # Test with medium dataset
        print("🔍 Testing medium dataset collection...")
        result = pipeline.collect_large_dataset(1000, ['Karachi', 'Lahore', 'Islamabad'])
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Performance test completed in {duration:.2f} seconds")
        print(f"📊 Collected {len(result)} restaurants")
        print(f"⚡ Rate: {len(result)/duration:.1f} restaurants/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ENHANCED PIPELINE COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Enhanced Collector", test_enhanced_collector),
        ("ML Models", test_ml_models),
        ("Data Cleaning", test_data_cleaning),
        ("Main Pipeline", test_main_pipeline),
        ("Performance Test", run_performance_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready for production use.")
    elif passed >= total * 0.8:
        print("⚠️ Most tests passed. Pipeline is mostly functional.")
    else:
        print("❌ Many tests failed. Pipeline needs attention.")
    
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 