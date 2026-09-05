import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import joblib
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class LeadScorer:
    def __init__(self, model_type: str = 'gradient_boosting'):
        self.model_type = model_type
        self.pipeline = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
        # Enhanced model configuration
        self.model_config = {
            'gradient_boosting': {
                'n_estimators': 300,
                'learning_rate': 0.1,
                'max_depth': 8,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'subsample': 0.8,
                'random_state': 42
            },
            'random_forest': {
                'n_estimators': 200,
                'max_depth': 15,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'max_features': 'sqrt',
                'random_state': 42
            },
            'xgboost': {
                'n_estimators': 500,
                'learning_rate': 0.05,
                'max_depth': 6,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
        }
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for lead scoring"""
        df_copy = df.copy()
        
        # Create feature columns
        features = []
        
        # 1. Data Completeness Score (0-100)
        completeness_score = self._calculate_completeness_score(df_copy)
        features.append(completeness_score)
        
        # 2. Online Presence Score (0-100)
        online_presence_score = self._calculate_online_presence_score(df_copy)
        features.append(online_presence_score)
        
        # 3. Rating Score (0-100)
        rating_score = self._calculate_rating_score(df_copy)
        features.append(rating_score)
        
        # 4. Reviews Score (0-100)
        reviews_score = self._calculate_reviews_count_score(df_copy)
        features.append(reviews_score)
        
        # 5. Source Reliability Score (0-100)
        source_score = self._calculate_source_score(df_copy)
        features.append(source_score)
        
        # 6. City Market Score (0-100)
        city_score = self._calculate_city_score(df_copy)
        features.append(city_score)
        
        # 7. Cuisine Popularity Score (0-100)
        cuisine_score = self._calculate_cuisine_score(df_copy)
        features.append(cuisine_score)
        
        # 8. Business Size Indicators
        business_size_score = self._calculate_business_size_score(df_copy)
        features.append(business_size_score)
        
        # 9. Contact Quality Score (0-100)
        contact_quality_score = self._calculate_contact_quality_score(df_copy)
        features.append(contact_quality_score)
        
        # 10. Social Media Presence Score (0-100)
        social_media_score = self._calculate_social_media_score(df_copy)
        features.append(social_media_score)
        
        # Create feature DataFrame
        feature_names = [
            'completeness_score', 'online_presence_score', 'rating_score',
            'reviews_score', 'source_score', 'city_score', 'cuisine_score',
            'business_size_score', 'contact_quality_score', 'social_media_score'
        ]
        
        feature_df = pd.DataFrame(dict(zip(feature_names, features)))
        
        # Add original columns that might be useful
        useful_columns = ['name', 'city', 'cuisine_type', 'rating', 'reviews_count', 'source']
        for col in useful_columns:
            if col in df_copy.columns:
                feature_df[col] = df_copy[col]
        
        return feature_df
    
    def _calculate_completeness_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate data completeness score"""
        score = 0
        
        # Name (required)
        score += df['name'].notna().astype(int) * 20
        
        # Phone (high value)
        score += df['phone'].notna().astype(int) * 25
        
        # Address (medium value)
        score += df['address'].notna().astype(int) * 20
        
        # Website (medium value)
        score += df['website'].notna().astype(int) * 15
        
        # Rating (low value)
        score += df['rating'].notna().astype(int) * 10
        
        # Description (low value)
        if 'description' in df.columns:
            score += df['description'].notna().astype(int) * 10
            
        return score
    
    def _calculate_online_presence_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate online presence score"""
        score = 0
        
        # Website presence
        score += df['website'].notna().astype(int) * 30
        
        # Social media presence (if available)
        if 'social_media' in df.columns:
            social_cols = ['facebook', 'instagram', 'twitter']
            for col in social_cols:
                if col in df['social_media'].iloc[0] if len(df) > 0 else {}:
                    score += df['social_media'].apply(lambda x: x.get(col, '') != '').astype(int) * 15
        
        # Food delivery platform presence
        if 'source' in df.columns:
            delivery_platforms = ['FoodPanda', 'Zomato', 'Uber Eats']
            for platform in delivery_platforms:
                score += (df['source'] == platform).astype(int) * 20
        
        return score
    
    def _calculate_rating_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate rating-based score"""
        if 'rating' not in df.columns:
            return pd.Series(0, index=df.index)
        
        # Convert rating to 0-100 scale
        rating_score = df['rating'].fillna(0) * 20  # 5-star rating * 20 = 100
        
        return rating_score
    
    def _calculate_reviews_count_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate reviews count score"""
        if 'reviews_count' not in df.columns:
            return pd.Series(0, index=df.index)
        
        # Normalize reviews count to 0-100 scale
        reviews = df['reviews_count'].fillna(0)
        
        # Log scale to handle outliers
        if reviews.max() > 0:
            reviews_score = np.log1p(reviews) / np.log1p(reviews.max()) * 100
        else:
            reviews_score = pd.Series(0, index=df.index)
        
        return reviews_score
    
    def _calculate_source_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate source reliability score"""
        if 'source' not in df.columns:
            return pd.Series(0, index=df.index)
        
        source_scores = {
            'Google Maps': 100,
            'FoodPanda': 80,
            'Yellow Pages PK': 70,
            'Facebook Pages': 60
        }
        
        return df['source'].map(source_scores).fillna(50)
    
    def _calculate_city_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate city market score based on population and economic activity"""
        if 'city' not in df.columns:
            return pd.Series(0, index=df.index)
        
        city_scores = {
            'Karachi': 100,      # Largest city, major economic hub
            'Lahore': 95,        # Second largest, cultural hub
            'Islamabad': 90,     # Capital city
            'Rawalpindi': 85,    # Twin city with Islamabad
            'Faisalabad': 80,    # Industrial city
            'Multan': 75,        # Historical city
            'Peshawar': 70,      # Provincial capital
            'Quetta': 65,        # Provincial capital
            'Gujranwala': 60,    # Industrial city
            'Sialkot': 55,       # Export hub
            'Bahawalpur': 50,    # Regional center
            'Sargodha': 45,      # Agricultural city
            'Jhang': 40,         # Regional center
            'Sheikhupura': 35,   # Industrial city
            'Rahim Yar Khan': 30, # Regional center
            'Gujrat': 25,        # Regional center
            'Kasur': 20,         # Regional center
            'Okara': 15,         # Regional center
            'Mianwali': 10,      # Regional center
            'Sahiwal': 5         # Regional center
        }
        
        return df['city'].map(city_scores).fillna(25)
    
    def _calculate_cuisine_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate cuisine popularity score"""
        if 'cuisine_type' not in df.columns:
            return pd.Series(0, index=df.index)
        
        cuisine_scores = {
            'Pakistani': 100,    # Most popular
            'BBQ': 95,           # Very popular
            'Fast Food': 90,     # High demand
            'Chinese': 85,       # Popular
            'Italian': 80,       # Popular
            'Indian': 75,        # Popular
            'Thai': 70,          # Growing popularity
            'Turkish': 65,       # Moderate popularity
            'Lebanese': 60,      # Moderate popularity
            'Mexican': 55,       # Moderate popularity
            'Japanese': 50,      # Moderate popularity
            'Korean': 45,        # Growing popularity
            'American': 40,      # Moderate popularity
            'European': 35,      # Moderate popularity
            'Fusion': 30,        # Niche
            'Desserts': 25,      # Niche
            'Beverages': 20      # Niche
        }
        
        return df['cuisine_type'].map(cuisine_scores).fillna(50)
    
    def _calculate_business_size_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate business size indicators score"""
        score = 0
        
        # Multiple locations (if available)
        if 'location' in df.columns:
            # Check if location data is meaningful
            has_location = df['location'].apply(lambda x: isinstance(x, dict) and x.get('lat', 0) != 0)
            score += has_location.astype(int) * 20
        
        # Chain indicators in name
        chain_keywords = ['chain', 'franchise', 'outlet', 'branch', 'restaurant']
        for keyword in chain_keywords:
            score += df['name'].str.contains(keyword, case=False, na=False).astype(int) * 10
        
        # Multiple sources (indicates larger presence)
        if 'source' in df.columns:
            # This is a simplified approach - in practice you'd track multiple sources per restaurant
            score += 10  # Base score for being in our database
        
        return score
    
    def _calculate_contact_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate contact information quality score"""
        score = 0
        
        # Phone number quality
        phone_quality = df['phone'].apply(lambda x: len(str(x)) >= 10 if pd.notna(x) else False)
        score += phone_quality.astype(int) * 40
        
        # Website quality
        website_quality = df['website'].apply(lambda x: 'http' in str(x) if pd.notna(x) else False)
        score += website_quality.astype(int) * 30
        
        # Address quality
        address_quality = df['address'].apply(lambda x: len(str(x)) > 10 if pd.notna(x) else False)
        score += address_quality.astype(int) * 30
        
        return score
    
    def _calculate_social_media_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate social media presence score"""
        score = 0
        
        if 'social_media' in df.columns:
            social_platforms = ['facebook', 'instagram', 'twitter', 'youtube', 'tiktok']
            
            for platform in social_platforms:
                if platform in df['social_media'].iloc[0] if len(df) > 0 else {}:
                    has_platform = df['social_media'].apply(lambda x: x.get(platform, '') != '')
                    score += has_platform.astype(int) * 20
        
        # Also check if website contains social media links
        if 'website' in df.columns:
            social_keywords = ['facebook.com', 'instagram.com', 'twitter.com', 'youtube.com']
            for keyword in social_keywords:
                score += df['website'].str.contains(keyword, case=False, na=False).astype(int) * 10
        
        return score
    
    def create_target_variable(self, df: pd.DataFrame) -> pd.Series:
        """Create target variable for training (lead potential score)"""
        # Combine all feature scores to create a target variable
        features_df = self.prepare_features(df)
        
        # Calculate weighted average of all scores
        feature_columns = [col for col in features_df.columns if col.endswith('_score')]
        
        if not feature_columns:
            return pd.Series(50, index=df.index)  # Default score
        
        # Weight different factors
        weights = {
            'completeness_score': 0.15,
            'online_presence_score': 0.20,
            'rating_score': 0.15,
            'reviews_score': 0.10,
            'source_score': 0.10,
            'city_score': 0.15,
            'cuisine_score': 0.05,
            'business_size_score': 0.05,
            'contact_quality_score': 0.03,
            'social_media_score': 0.02
        }
        
        target_score = pd.Series(0, index=df.index)
        
        for feature in feature_columns:
            if feature in weights and feature in features_df.columns:
                target_score += features_df[feature] * weights[feature]
        
        return target_score
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train the lead scoring model"""
        print("Preparing training data...")
        
        # Prepare features
        features_df = self.prepare_features(df)
        
        # Create target variable
        target = self.create_target_variable(df)
        
        # Remove non-numeric columns for training
        numeric_features = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_features]
        y = target
        
        if len(X) < 10:
            print("Insufficient training data. Need at least 10 samples.")
            return {'r2_score': 0, 'status': 'insufficient_data'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Create pipeline
        if self.model_type == 'random_forest':
            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])
        elif self.model_type == 'gradient_boosting':
            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', GradientBoostingRegressor(n_estimators=100, random_state=42))
            ])
        elif self.model_type == 'linear':
            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', LinearRegression())
            ])
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Train the model
        print(f"Training {self.model_type} lead scorer...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.pipeline, X, y, cv=5, scoring='r2')
        
        print(f"Model trained successfully!")
        print(f"R² Score: {r2:.3f}")
        print(f"Mean Squared Error: {mse:.3f}")
        print(f"Mean Absolute Error: {mae:.3f}")
        print(f"Cross-validation R²: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        return {
            'r2_score': r2,
            'mse': mse,
            'mae': mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'status': 'success'
        }
    
    def predict_lead_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict lead scores for restaurants"""
        if self.pipeline is None:
            print("Model not trained. Using rule-based scoring instead.")
            return self._rule_based_scoring(df)
        
        print("Predicting lead scores using ML model...")
        
        # Prepare features
        features_df = self.prepare_features(df)
        
        # Get numeric features
        numeric_features = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_features]
        
        # Predict
        predicted_scores = self.pipeline.predict(X)
        
        # Update dataframe
        df_copy = df.copy()
        df_copy['predicted_lead_score'] = predicted_scores
        df_copy['lead_score'] = predicted_scores.round(1)
        
        # Add lead potential category
        df_copy['lead_potential'] = df_copy['lead_score'].apply(self._categorize_lead_potential)
        
        return df_copy
    
    def _rule_based_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fallback rule-based lead scoring"""
        print("Using rule-based lead scoring...")
        
        df_copy = df.copy()
        
        # Calculate basic score
        features_df = self.prepare_features(df)
        target = self.create_target_variable(df)
        
        df_copy['predicted_lead_score'] = target
        df_copy['lead_score'] = target.round(1)
        df_copy['lead_potential'] = df_copy['lead_score'].apply(self._categorize_lead_potential)
        
        return df_copy
    
    def _categorize_lead_potential(self, score: float) -> str:
        """Categorize lead potential based on score"""
        if score >= 80:
            return 'High Potential'
        elif score >= 60:
            return 'Medium Potential'
        elif score >= 40:
            return 'Low Potential'
        else:
            return 'Poor Potential'
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        if self.pipeline is None:
            raise ValueError("No trained model to save")
        
        joblib.dump(self.pipeline, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        self.pipeline = joblib.load(filepath)
        print(f"Model loaded from {filepath}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance (for tree-based models only)"""
        if self.pipeline is None or self.model_type not in ['random_forest', 'gradient_boosting']:
            return {}
        
        # Get feature names
        feature_names = self.pipeline.named_steps['scaler'].get_feature_names_out()
        
        # Get feature importance from regressor
        regressor = self.pipeline.named_steps['regressor']
        importances = regressor.feature_importances_
        
        # Create feature importance dictionary
        feature_importance = dict(zip(feature_names, importances))
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_features) 