#!/usr/bin/env python3
"""
Enhanced Data Collector for Restaurant Lead Generation
Combines multiple sources and handles large datasets efficiently
"""

import time
import random
import asyncio
import aiohttp
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PAKISTAN_CITIES, CUISINE_TYPES, BATCH_SIZE, DELAY_BETWEEN_REQUESTS
from data_collectors.demo_collector import DemoCollector
from data_collectors.google_maps_collector import GoogleMapsCollector
from data_collectors.yellow_pages_collector import YellowPagesCollector
from data_collectors.facebook_collector import FacebookCollector
from data_collectors.foodpanda_collector import FoodPandaCollector

class EnhancedCollector:
    """Enhanced collector that combines multiple sources and handles large datasets"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.collectors = {}
        self.demo_collector = DemoCollector("Enhanced Demo")
        self._initialize_collectors()
        
    def _initialize_collectors(self):
        """Initialize all available collectors"""
        # Demo collector (always available)
        self.collectors['demo'] = self.demo_collector
        
        # Try to initialize other collectors
        try:
            from config import GOOGLE_MAPS_API_KEY
            if GOOGLE_MAPS_API_KEY:
                self.collectors['google_maps'] = GoogleMapsCollector(GOOGLE_MAPS_API_KEY)
        except:
            pass
            
        try:
            self.collectors['yellow_pages'] = YellowPagesCollector()
        except:
            pass
            
        try:
            from config import FACEBOOK_ACCESS_TOKEN
            if FACEBOOK_ACCESS_TOKEN:
                self.collectors['facebook'] = FacebookCollector(FACEBOOK_ACCESS_TOKEN)
        except:
            pass
            
        try:
            self.collectors['foodpanda'] = FoodPandaCollector()
        except:
            pass
    
    def collect_large_dataset(self, cities: List[str] = None, target_total: int = 10000) -> List[Dict]:
        """Collect large dataset using multiple sources and parallel processing"""
        if cities is None:
            cities = PAKISTAN_CITIES[:15]  # Use more cities for larger dataset
        
        print(f"🎯 Target: {target_total:,} restaurants from {len(cities)} cities")
        print(f"🔍 Available sources: {list(self.collectors.keys())}")
        
        all_restaurants = []
        restaurants_per_city = max(1, target_total // len(cities))
        
        # Use ThreadPoolExecutor for parallel collection
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit collection tasks for each city
            future_to_city = {
                executor.submit(self._collect_city_data, city, restaurants_per_city): city 
                for city in cities
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    city_restaurants = future.result()
                    all_restaurants.extend(city_restaurants)
                    print(f"✅ {city}: {len(city_restaurants)} restaurants collected")
                except Exception as e:
                    print(f"❌ {city}: Error - {str(e)}")
        
        # Remove duplicates
        unique_restaurants = self._remove_duplicates(all_restaurants)
        
        print(f"\n🎉 Collection completed!")
        print(f"📊 Total collected: {len(all_restaurants):,}")
        print(f"🔍 Unique restaurants: {len(unique_restaurants):,}")
        print(f"🚫 Duplicates removed: {len(all_restaurants) - len(unique_restaurants):,}")
        
        return unique_restaurants
    
    def _collect_city_data(self, city: str, target_per_city: int) -> List[Dict]:
        """Collect data for a specific city using multiple sources"""
        city_restaurants = []
        
        # Distribute target across available sources
        sources = list(self.collectors.keys())
        target_per_source = max(1, target_per_city // len(sources))
        
        for source_name in sources:
            try:
                collector = self.collectors[source_name]
                print(f"  🔍 {city} - {source_name}: Collecting {target_per_source} restaurants...")
                
                # Collect from source
                if source_name == 'demo':
                    restaurants = collector.search_restaurants(city, target_per_source)
                else:
                    restaurants = collector.search_restaurants(city, target_per_source)
                
                if restaurants:
                    city_restaurants.extend(restaurants)
                    print(f"    ✓ {source_name}: {len(restaurants)} restaurants found")
                else:
                    print(f"    ⚠ {source_name}: No restaurants found")
                    
                # Add delay between sources
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except Exception as e:
                print(f"    ❌ {source_name}: Error - {str(e)}")
                continue
        
        # Remove duplicates within city
        unique_city_restaurants = self._remove_city_duplicates(city_restaurants)
        
        return unique_city_restaurants
    
    def _remove_city_duplicates(self, restaurants: List[Dict]) -> List[Dict]:
        """Remove duplicate restaurants within a city"""
        if not restaurants:
            return restaurants
        
        seen = set()
        unique_restaurants = []
        
        for restaurant in restaurants:
            # Create unique identifier
            name = restaurant.get('name', '').lower().strip()
            city = restaurant.get('city', '').lower().strip()
            phone = restaurant.get('phone', '').strip()
            
            if phone:
                identifier = f"{name}_{city}_{phone}"
            else:
                identifier = f"{name}_{city}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_restaurants.append(restaurant)
        
        return unique_restaurants
    
    def _remove_duplicates(self, restaurants: List[Dict]) -> List[Dict]:
        """Remove duplicate restaurants across all cities"""
        if not restaurants:
            return restaurants
        
        seen = set()
        unique_restaurants = []
        
        for restaurant in restaurants:
            name = restaurant.get('name', '').lower().strip()
            city = restaurant.get('city', '').lower().strip()
            phone = restaurant.get('phone', '').strip()
            
            if phone:
                identifier = f"{name}_{city}_{phone}"
            else:
                identifier = f"{name}_{city}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_restaurants.append(restaurant)
        
        return unique_restaurants
    
    def collect_with_fallback(self, cities: List[str] = None, target_total: int = 10000) -> List[Dict]:
        """Collect data with fallback to demo data if other sources fail"""
        try:
            # Try to collect from real sources first
            restaurants = self.collect_large_dataset(cities, target_total)
            
            # If we don't have enough data, supplement with demo data
            if len(restaurants) < target_total * 0.8:  # Less than 80% of target
                print(f"\n⚠️ Insufficient data from real sources. Supplementing with demo data...")
                
                remaining_target = target_total - len(restaurants)
                demo_restaurants = self.demo_collector.search_restaurants(
                    cities[0] if cities else 'Karachi', 
                    remaining_target
                )
                
                restaurants.extend(demo_restaurants)
                print(f"✅ Added {len(demo_restaurants)} demo restaurants")
            
            return restaurants
            
        except Exception as e:
            print(f"❌ Error in main collection. Falling back to demo data: {str(e)}")
            return self.demo_collector.search_restaurants(
                cities[0] if cities else 'Karachi', 
                target_total
            )
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about available collectors and their status"""
        stats = {
            'total_sources': len(self.collectors),
            'available_sources': list(self.collectors.keys()),
            'demo_available': 'demo' in self.collectors,
            'google_maps_available': 'google_maps' in self.collectors,
            'yellow_pages_available': 'yellow_pages' in self.collectors,
            'facebook_available': 'facebook' in self.collectors,
            'foodpanda_available': 'foodpanda' in self.collectors
        }
        
        return stats 