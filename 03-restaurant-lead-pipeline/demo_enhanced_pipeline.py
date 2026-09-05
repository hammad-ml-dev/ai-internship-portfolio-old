#!/usr/bin/env python3
"""
Enhanced Pipeline Demo Script
Showcases the enhanced restaurant lead generation capabilities
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_enhanced_collector():
    """Demo the enhanced collector capabilities"""
    print("🎯 DEMO: Enhanced Data Collector")
    print("=" * 50)
    
    try:
        from data_collectors.enhanced_collector import EnhancedCollector
        
        # Initialize collector
        collector = EnhancedCollector(max_workers=4)
        stats = collector.get_collection_stats()
        
        print(f"📊 Available sources: {', '.join(stats['available_sources'])}")
        print(f"🔍 Total sources: {stats['total_sources']}")
        
        # Demo small collection
        print(f"\n🚀 Demo: Collecting 200 restaurants from Karachi and Lahore...")
        start_time = time.time()
        
        restaurants = collector.collect_large_dataset(['Karachi', 'Lahore'], 200)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Collection completed in {duration:.2f} seconds")
        print(f"📊 Total restaurants: {len(restaurants)}")
        print(f"⚡ Rate: {len(restaurants)/duration:.1f} restaurants/second")
        
        # Show sample data
        if restaurants:
            print(f"\n📋 Sample restaurant data:")
            for i, restaurant in enumerate(restaurants[:3]):
                print(f"  {i+1}. {restaurant.get('name', 'N/A')}")
                print(f"     City: {restaurant.get('city', 'N/A')}")
                print(f"     Cuisine: {restaurant.get('cuisine_type', 'N/A')}")
                print(f"     Rating: {restaurant.get('rating', 'N/A')}")
                print(f"     Lead Score: {restaurant.get('lead_score', 'N/A')}")
                print()
        
        return restaurants
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return []

def demo_ml_models():
    """Demo the ML model capabilities"""
    print("🤖 DEMO: Machine Learning Models")
    print("=" * 50)
    
    try:
        from ml_models.cuisine_classifier import CuisineClassifier
        from ml_models.lead_scorer import LeadScorer
        
        # Initialize models
        print("🔧 Initializing ML models...")
        classifier = CuisineClassifier('random_forest')
        scorer = LeadScorer('gradient_boosting')
        
        print(f"✅ Cuisine Classifier: {classifier.model_type}")
        print(f"✅ Lead Scorer: {scorer.model_type}")
        
        # Show model configurations
        print(f"\n📊 Cuisine Classifier Config:")
        for key, value in classifier.model_config['random_forest'].items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 Lead Scorer Config:")
        for key, value in scorer.model_config['gradient_boosting'].items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML demo failed: {str(e)}")
        return False

def demo_pipeline_integration():
    """Demo the full pipeline integration"""
    print("🔗 DEMO: Pipeline Integration")
    print("=" * 50)
    
    try:
        from main_pipeline import RestaurantLeadPipeline
        
        # Initialize pipeline
        print("🔧 Initializing enhanced pipeline...")
        pipeline = RestaurantLeadPipeline()
        
        print("✅ Pipeline initialized successfully")
        print(f"🔍 Enhanced collector: {pipeline.enhanced_collector.__class__.__name__}")
        print(f"🧹 Data cleaner: {pipeline.cleaner.__class__.__name__}")
        print(f"🍽️ Cuisine classifier: {pipeline.cuisine_classifier.__class__.__name__}")
        print(f"📊 Lead scorer: {pipeline.lead_scorer.__class__.__name__}")
        print(f"📤 Data exporter: {pipeline.exporter.__class__.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline demo failed: {str(e)}")
        return False

def demo_large_scale_capability():
    """Demo the large-scale collection capability"""
    print("🚀 DEMO: Large-Scale Collection Capability")
    print("=" * 50)
    
    try:
        from main_pipeline import RestaurantLeadPipeline
        
        pipeline = RestaurantLeadPipeline()
        
        print("🎯 Target: 1,000 restaurants (demo of large-scale capability)")
        print("🌍 Cities: Karachi, Lahore, Islamabad")
        print("⏱️ Estimated time: 2-5 minutes")
        
        # Ask user if they want to proceed
        response = input("\n❓ Do you want to run this demo? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            print("\n🚀 Starting large-scale collection demo...")
            start_time = time.time()
            
            restaurants = pipeline.collect_large_dataset(1000, ['Karachi', 'Lahore', 'Islamabad'])
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n✅ Large-scale demo completed!")
            print(f"📊 Total restaurants: {len(restaurants):,}")
            print(f"⏱️ Duration: {duration:.2f} seconds")
            print(f"⚡ Rate: {len(restaurants)/duration:.1f} restaurants/second")
            
            return restaurants
        else:
            print("⏭️ Skipping large-scale demo")
            return []
        
    except Exception as e:
        print(f"❌ Large-scale demo failed: {str(e)}")
        return []

def main():
    """Run all demos"""
    print("🎉 ENHANCED RESTAURANT LEAD GENERATION PIPELINE DEMO")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This demo showcases the enhanced pipeline capabilities for generating 10k+ leads")
    
    demos = [
        ("Enhanced Collector", demo_enhanced_collector),
        ("ML Models", demo_ml_models),
        ("Pipeline Integration", demo_pipeline_integration),
        ("Large-Scale Capability", demo_large_scale_capability)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*70}")
        print(f"🎬 Running: {demo_name}")
        print(f"{'='*70}")
        
        try:
            result = demo_func()
            results.append((demo_name, True, result))
            print(f"✅ {demo_name} demo completed successfully")
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {str(e)}")
            results.append((demo_name, False, None))
        
        # Add delay between demos
        if demo_name != demos[-1][0]:  # Not the last demo
            print("\n⏳ Waiting 3 seconds before next demo...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 DEMO RESULTS SUMMARY")
    print(f"{'='*70}")
    
    passed = 0
    total = len(results)
    
    for demo_name, success, result in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {demo_name}")
        if success and result:
            if isinstance(result, list):
                print(f"    📊 Generated {len(result)} restaurants")
            elif isinstance(result, bool):
                print(f"    ✅ Component working")
        if not success:
            print(f"    ❌ Demo failed")
    
    print(f"\n🎯 Overall: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos passed! The enhanced pipeline is working perfectly.")
        print("🚀 Ready to generate 10,000+ restaurant leads!")
    elif passed >= total * 0.8:
        print("⚠️ Most demos passed. The pipeline is mostly functional.")
    else:
        print("❌ Many demos failed. The pipeline needs attention.")
    
    print(f"\n💡 Next steps:")
    print(f"   • Run: python main_pipeline.py --large")
    print(f"   • Test: python test_enhanced_pipeline.py")
    print(f"   • Web: cd web_app && python app.py")
    
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 