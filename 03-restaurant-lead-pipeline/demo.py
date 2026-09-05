#!/usr/bin/env python3
"""
Demo script for the Restaurant Lead Generation Pipeline
Shows how the pipeline works with sample data
"""

import pandas as pd
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_cleaning.cleaner import RestaurantDataCleaner
from ml_models.cuisine_classifier import CuisineClassifier
from ml_models.lead_scorer import LeadScorer
from exporters.data_exporter import DataExporter

def create_sample_data():
    """Create sample restaurant data for demonstration"""
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
            'source': 'Google Maps',
            'description': 'Best BBQ restaurant in Karachi'
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
            'source': 'FoodPanda',
            'description': 'BBQ restaurant with delivery service'
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
            'source': 'Yellow Pages PK',
            'description': 'Authentic Chinese cuisine'
        },
        {
            'name': 'Pizza Hut',
            'city': 'Islamabad',
            'address': 'Blue Area, Islamabad',
            'phone': '051-1234567',
            'website': 'https://pizzahut.pk',
            'rating': 4.0,
            'reviews_count': 200,
            'cuisine_type': 'Italian',
            'source': 'Google Maps',
            'description': 'International pizza chain'
        },
        {
            'name': 'Thai Spice',
            'city': 'Karachi',
            'address': 'Clifton, Karachi',
            'phone': '021-1234567',
            'website': 'thaispice.com',
            'rating': 4.7,
            'reviews_count': 75,
            'cuisine_type': 'Thai',
            'source': 'Facebook Pages',
            'description': 'Traditional Thai food'
        },
        {
            'name': 'Desi Dhaba',
            'city': 'Lahore',
            'address': 'Food Street, Lahore',
            'phone': '042-9876543',
            'website': '',
            'rating': 4.3,
            'reviews_count': 120,
            'cuisine_type': 'Pakistani',
            'source': 'Yellow Pages PK',
            'description': 'Local Pakistani food'
        },
        {
            'name': 'Burger House',
            'city': 'Rawalpindi',
            'address': 'Mall Road, Rawalpindi',
            'phone': '051-5555555',
            'website': 'burgerhouse.pk',
            'rating': 3.8,
            'reviews_count': 45,
            'cuisine_type': 'Fast Food',
            'source': 'FoodPanda',
            'description': 'Fast food burgers and fries'
        },
        {
            'name': 'Sushi Bar',
            'city': 'Karachi',
            'address': 'Defence, Karachi',
            'phone': '021-9999999',
            'website': 'sushibar.com',
            'rating': 4.6,
            'reviews_count': 60,
            'cuisine_type': 'Japanese',
            'source': 'Google Maps',
            'description': 'Fresh sushi and Japanese cuisine'
        }
    ]
    
    return sample_restaurants

def run_demo():
    """Run the complete demo pipeline"""
    print("🍕 Restaurant Lead Generation Pipeline - Demo")
    print("=" * 60)
    
    # Step 1: Create sample data
    print("\n📊 Step 1: Creating sample restaurant data...")
    sample_data = create_sample_data()
    print(f"✓ Created {len(sample_data)} sample restaurants")
    
    # Show sample data
    print("\nSample data:")
    df_sample = pd.DataFrame(sample_data)
    print(df_sample[['name', 'city', 'cuisine_type', 'rating', 'source']].head())
    
    # Step 2: Data Cleaning
    print("\n🧹 Step 2: Data cleaning and deduplication...")
    cleaner = RestaurantDataCleaner()
    cleaned_df = cleaner.clean_dataset(sample_data)
    
    print(f"✓ Data cleaning completed!")
    print(f"  - Original records: {len(sample_data)}")
    print(f"  - Cleaned records: {len(cleaned_df)}")
    print(f"  - Duplicates removed: {len(sample_data) - len(cleaned_df)}")
    
    # Show cleaned data
    print("\nCleaned data:")
    print(cleaned_df[['name', 'city', 'phone', 'cuisine_type', 'quality_score']].head())
    
    # Step 3: Cuisine Classification
    print("\n🍽️ Step 3: ML-powered cuisine classification...")
    classifier = CuisineClassifier(model_type='naive_bayes')
    
    # Train the classifier
    print("Training cuisine classifier...")
    training_result = classifier.train(cleaned_df)
    
    if training_result['status'] == 'success':
        print(f"✓ Cuisine classifier trained successfully!")
        print(f"  - Accuracy: {training_result['accuracy']:.3f}")
        
        # Classify restaurants
        classified_df = classifier.classify_restaurants(cleaned_df)
        
        # Show classification results
        print("\nClassification results:")
        if 'predicted_cuisine' in classified_df.columns:
            print(classified_df[['name', 'cuisine_type', 'predicted_cuisine', 'classification_confidence']].head())
    else:
        print("⚠ Cuisine classification training failed, using rule-based")
        classified_df = cleaned_df
    
    # Step 4: Lead Scoring
    print("\n📊 Step 4: Intelligent lead scoring...")
    scorer = LeadScorer(model_type='random_forest')
    
    # Train the scorer
    print("Training lead scorer...")
    training_result = scorer.train(classified_df)
    
    if training_result['status'] == 'success':
        print(f"✓ Lead scorer trained successfully!")
        print(f"  - R² Score: {training_result['r2_score']:.3f}")
        
        # Score leads
        scored_df = scorer.predict_lead_score(classified_df)
        
        # Show scoring results
        print("\nLead scoring results:")
        if 'lead_score' in scored_df.columns:
            print(scored_df[['name', 'city', 'quality_score', 'lead_score', 'lead_potential']].head())
            
            # Show high potential leads
            high_potential = scored_df[scored_df['lead_score'] >= 70]
            if len(high_potential) > 0:
                print(f"\n🎯 High potential leads (score >= 70): {len(high_potential)}")
                print(high_potential[['name', 'city', 'lead_score', 'lead_potential']].head())
    else:
        print("⚠ Lead scoring training failed, using rule-based")
        scored_df = classified_df
    
    # Step 5: Data Export
    print("\n📤 Step 5: Exporting data to multiple formats...")
    exporter = DataExporter(output_dir="demo_output")
    
    # Export to all formats
    export_files = exporter.export_all_formats(scored_df, "demo_restaurants")
    
    print(f"✓ Data export completed!")
    print(f"  - Export files: {len(export_files)}")
    for format_type, filepath in export_files.items():
        print(f"    - {format_type.upper()}: {os.path.basename(filepath)}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Final dataset: {len(scored_df)} restaurants")
    print(f"Export files: {len(export_files)} formats")
    
    # Show final dataset summary
    if 'lead_score' in scored_df.columns:
        print(f"\n📈 Lead Scoring Summary:")
        print(f"  - High Potential: {(scored_df['lead_score'] >= 80).sum()}")
        print(f"  - Medium Potential: {((scored_df['lead_score'] >= 60) & (scored_df['lead_score'] < 80)).sum()}")
        print(f"  - Low Potential: {((scored_df['lead_score'] >= 40) & (scored_df['lead_score'] < 60)).sum()}")
        print(f"  - Poor Potential: {(scored_df['lead_score'] < 40).sum()}")
    
    if 'cuisine_type' in scored_df.columns:
        print(f"\n🍽️ Cuisine Distribution:")
        cuisine_counts = scored_df['cuisine_type'].value_counts()
        for cuisine, count in cuisine_counts.head().items():
            print(f"  - {cuisine}: {count}")
    
    print(f"\n🏙️ Cities Covered: {scored_df['city'].nunique()}")
    print(f"📊 Data Sources: {scored_df['source'].nunique()}")
    
    return scored_df

if __name__ == "__main__":
    run_demo() 