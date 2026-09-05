import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import phonenumbers
from config import PAKISTAN_CITIES

class RestaurantDataCleaner:
    def __init__(self):
        self.city_mappings = self._create_city_mappings()
        
    def clean_dataset(self, restaurants: List[Dict]) -> pd.DataFrame:
        """Clean and prepare the restaurant dataset"""
        # Convert to DataFrame
        df = pd.DataFrame(restaurants)
        
        if df.empty:
            return df
            
        # Clean each column
        df = self._clean_names(df)
        df = self._clean_cities(df)
        df = self._clean_phone_numbers(df)
        df = self._clean_addresses(df)
        df = self._clean_websites(df)
        df = self._clean_ratings(df)
        df = self._clean_cuisine_types(df)
        
        # Remove duplicates
        df = self._remove_duplicates(df)
        
        # Add quality scores
        df = self._add_quality_scores(df)
        
        return df
    
    def _clean_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean restaurant names"""
        if 'name' not in df.columns:
            return df
            
        # Remove extra whitespace and normalize
        df['name'] = df['name'].str.strip()
        df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['restaurant', 'cafe', 'diner', 'grill', 'kitchen']
        for prefix in prefixes_to_remove:
            df['name'] = df['name'].str.replace(f'^{prefix}\s+', '', case=False, regex=True)
            df['name'] = df['name'].str.replace(f'\s+{prefix}$', '', case=False, regex=True)
        
        # Remove special characters but keep spaces and basic punctuation
        df['name'] = df['name'].str.replace(r'[^\w\s\-&\.]', '', regex=True)
        
        return df
    
    def _clean_cities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize city names"""
        if 'city' not in df.columns:
            return df
            
        # Standardize city names
        df['city'] = df['city'].str.strip()
        df['city'] = df['city'].str.title()
        
        # Map variations to standard names
        for standard_name, variations in self.city_mappings.items():
            for variation in variations:
                df.loc[df['city'].str.contains(variation, case=False, na=False), 'city'] = standard_name
        
        # Keep only valid Pakistan cities
        valid_cities = set(PAKISTAN_CITIES)
        df = df[df['city'].isin(valid_cities)]
        
        return df
    
    def _clean_phone_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize phone numbers"""
        if 'phone' not in df.columns:
            return df
            
        def clean_phone(phone):
            if pd.isna(phone) or phone == '':
                return ''
                
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', str(phone))
            
            # Handle Pakistan phone numbers
            if digits_only.startswith('92'):
                # Remove country code if present
                digits_only = digits_only[2:]
            
            if digits_only.startswith('0'):
                # Remove leading zero
                digits_only = digits_only[1:]
                
            # Validate length (Pakistan mobile numbers are 10 digits)
            if len(digits_only) == 10:
                return f"+92{digits_only}"
            elif len(digits_only) == 11 and digits_only.startswith('3'):
                return f"+92{digits_only}"
            else:
                return str(phone)  # Return original if can't parse
                
        df['phone'] = df['phone'].apply(clean_phone)
        
        return df
    
    def _clean_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize addresses"""
        if 'address' not in df.columns:
            return df
            
        # Remove extra whitespace
        df['address'] = df['address'].str.strip()
        df['address'] = df['address'].str.replace(r'\s+', ' ', regex=True)
        
        # Remove common address prefixes
        prefixes_to_remove = ['address:', 'location:', 'address -', 'location -']
        for prefix in prefixes_to_remove:
            df['address'] = df['address'].str.replace(f'^{prefix}\s*', '', case=False, regex=True)
        
        return df
    
    def _clean_websites(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize website URLs"""
        if 'website' not in df.columns:
            return df
            
        def clean_website(url):
            if pd.isna(url) or url == '':
                return ''
                
            url = str(url).strip()
            
            # Add protocol if missing
            if url and not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Remove trailing slashes
            url = url.rstrip('/')
            
            return url
            
        df['website'] = df['website'].apply(clean_website)
        
        return df
    
    def _clean_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate ratings"""
        if 'rating' not in df.columns:
            return df
            
        # Convert to numeric, handling errors
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Ensure ratings are between 0 and 5
        df['rating'] = df['rating'].clip(0, 5)
        
        # Fill missing ratings with 0
        df['rating'] = df['rating'].fillna(0)
        
        return df
    
    def _clean_cuisine_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize cuisine types"""
        if 'cuisine_type' not in df.columns:
            return df
            
        # Standardize cuisine types
        df['cuisine_type'] = df['cuisine_type'].str.strip()
        df['cuisine_type'] = df['cuisine_type'].str.title()
        
        # Map variations to standard types
        cuisine_mappings = {
            'Pakistani': ['Pakistani', 'Pak', 'Local', 'Traditional'],
            'BBQ': ['BBQ', 'Barbecue', 'Grill', 'Grilled'],
            'Chinese': ['Chinese', 'China', 'Szechuan', 'Cantonese'],
            'Fast Food': ['Fast Food', 'Fastfood', 'Quick Service', 'Fast'],
            'Italian': ['Italian', 'Italy', 'Pizza', 'Pasta'],
            'Thai': ['Thai', 'Thailand'],
            'Indian': ['Indian', 'India', 'Subcontinental'],
            'Turkish': ['Turkish', 'Turkey'],
            'Lebanese': ['Lebanese', 'Lebanon', 'Middle Eastern'],
            'Mexican': ['Mexican', 'Mexico', 'Tex-Mex'],
            'Japanese': ['Japanese', 'Japan', 'Sushi'],
            'Korean': ['Korean', 'Korea'],
            'American': ['American', 'USA', 'United States'],
            'European': ['European', 'Europe', 'Continental'],
            'Fusion': ['Fusion', 'Fusion Cuisine', 'Mixed'],
            'Desserts': ['Desserts', 'Dessert', 'Sweet', 'Bakery'],
            'Beverages': ['Beverages', 'Drinks', 'Cafe', 'Coffee', 'Tea']
        }
        
        for standard_type, variations in cuisine_mappings.items():
            for variation in variations:
                df.loc[df['cuisine_type'].str.contains(variation, case=False, na=False), 'cuisine_type'] = standard_type
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate restaurants using fuzzy matching"""
        if df.empty:
            return df
            
        # First, remove exact duplicates
        df = df.drop_duplicates(subset=['name', 'city', 'phone'], keep='first')
        
        # Then, remove fuzzy duplicates based on name similarity
        df = self._remove_fuzzy_duplicates(df)
        
        return df
    
    def _remove_fuzzy_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove restaurants with similar names in the same city"""
        if df.empty:
            return df
            
        # Group by city to check duplicates within each city
        cities = df['city'].unique()
        cleaned_dfs = []
        
        for city in cities:
            city_df = df[df['city'] == city].copy()
            
            if len(city_df) <= 1:
                cleaned_dfs.append(city_df)
                continue
                
            # Sort by name for consistent processing
            city_df = city_df.sort_values('name')
            
            # Check for similar names
            to_remove = set()
            
            for i in range(len(city_df)):
                if i in to_remove:
                    continue
                    
                name1 = city_df.iloc[i]['name']
                
                for j in range(i + 1, len(city_df)):
                    if j in to_remove:
                        continue
                        
                    name2 = city_df.iloc[j]['name']
                    
                    # Calculate similarity
                    similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                    
                    # If names are very similar (80%+), remove the second one
                    if similarity > 0.8:
                        to_remove.add(j)
            
            # Remove duplicates
            city_df = city_df.drop(city_df.index[list(to_remove)])
            cleaned_dfs.append(city_df)
        
        # Combine all cities
        return pd.concat(cleaned_dfs, ignore_index=True)
    
    def _add_quality_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add quality scores for each restaurant"""
        if df.empty:
            return df
            
        # Initialize quality score
        df['quality_score'] = 0
        
        # Score based on data completeness
        df['quality_score'] += df['name'].notna().astype(int) * 10
        df['quality_score'] += df['phone'].notna().astype(int) * 15
        df['quality_score'] += df['address'].notna().astype(int) * 10
        df['quality_score'] += df['website'].notna().astype(int) * 10
        df['quality_score'] += df['rating'].notna().astype(int) * 5
        
        # Score based on rating
        df['quality_score'] += df['rating'] * 2
        
        # Score based on reviews count (if available)
        if 'reviews_count' in df.columns:
            df['quality_score'] += df['reviews_count'].clip(0, 100) * 0.1
        
        # Score based on source reliability
        source_scores = {
            'Google Maps': 20,
            'FoodPanda': 15,
            'Yellow Pages PK': 10,
            'Facebook Pages': 5
        }
        
        df['quality_score'] += df['source'].map(source_scores).fillna(0)
        
        # Normalize score to 0-100
        df['quality_score'] = df['quality_score'].clip(0, 100)
        
        return df
    
    def _create_city_mappings(self) -> Dict[str, List[str]]:
        """Create mappings for city name variations"""
        return {
            'Karachi': ['karachi', 'khi', 'karachi city', 'port city'],
            'Lahore': ['lahore', 'lhr', 'lahore city', 'city of gardens'],
            'Islamabad': ['islamabad', 'isb', 'islamabad city', 'federal capital'],
            'Rawalpindi': ['rawalpindi', 'rwp', 'rawalpindi city', 'pindi'],
            'Faisalabad': ['faisalabad', 'fsd', 'faisalabad city', 'lyallpur'],
            'Multan': ['multan', 'mul', 'multan city', 'city of saints'],
            'Peshawar': ['peshawar', 'pwr', 'peshawar city', 'city of flowers'],
            'Quetta': ['quetta', 'qta', 'quetta city', 'fruit garden'],
            'Gujranwala': ['gujranwala', 'gjr', 'gujranwala city'],
            'Sialkot': ['sialkot', 'skt', 'sialkot city'],
            'Bahawalpur': ['bahawalpur', 'bwp', 'bahawalpur city'],
            'Sargodha': ['sargodha', 'srg', 'sargodha city'],
            'Jhang': ['jhang', 'jng', 'jhang city'],
            'Sheikhupura': ['sheikhupura', 'shp', 'sheikhupura city'],
            'Rahim Yar Khan': ['rahim yar khan', 'ryk', 'rahim yar khan city'],
            'Gujrat': ['gujrat', 'gjt', 'gujrat city'],
            'Kasur': ['kasur', 'ksr', 'kasur city'],
            'Okara': ['okara', 'okr', 'okara city'],
            'Mianwali': ['mianwali', 'mwl', 'mianwali city'],
            'Sahiwal': ['sahiwal', 'shw', 'sahiwal city']
        } 