import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import re
from typing import List, Dict, Tuple
from config import CUISINE_TYPES
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class CuisineClassifier:
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.pipeline = None
        self.vectorizer = None
        self.classifier = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Add cuisine-specific stop words
        self.stop_words.update(['restaurant', 'food', 'dining', 'eat', 'meal', 'dish', 'cuisine'])
        
        # Enhanced model configuration
        self.model_config = {
            'random_forest': {
                'n_estimators': 200,
                'max_features': 5000,
                'max_depth': 15,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42
            },
            'gradient_boosting': {
                'n_estimators': 300,
                'learning_rate': 0.1,
                'max_depth': 8,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42
            }
        }
        
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Prepare training data from the restaurant dataset"""
        texts = []
        labels = []
        
        for _, row in df.iterrows():
            # Combine name, description, and other text fields
            text_parts = []
            
            if pd.notna(row.get('name')):
                text_parts.append(str(row['name']))
            
            if pd.notna(row.get('description')):
                text_parts.append(str(row['description']))
                
            if pd.notna(row.get('cuisine_type')):
                text_parts.append(str(row['cuisine_type']))
            
            # Combine all text
            combined_text = ' '.join(text_parts)
            
            if combined_text.strip() and pd.notna(row.get('cuisine_type')):
                texts.append(combined_text)
                labels.append(row['cuisine_type'])
        
        return texts, labels
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for classification"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train the cuisine classifier"""
        print("Preparing training data...")
        texts, labels = self.prepare_training_data(df)
        
        if len(texts) < 10:
            print("Insufficient training data. Need at least 10 samples.")
            return {'accuracy': 0, 'status': 'insufficient_data'}
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Create pipeline
        if self.model_type == 'naive_bayes':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])
        elif self.model_type == 'random_forest':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Train the model
        print(f"Training {self.model_type} classifier...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.pipeline, processed_texts, labels, cv=5)
        
        print(f"Model trained successfully!")
        print(f"Test Accuracy: {accuracy:.3f}")
        print(f"Cross-validation scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'status': 'success'
        }
    
    def predict_cuisine(self, text: str) -> Tuple[str, float]:
        """Predict cuisine type for given text"""
        if self.pipeline is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Predict
        prediction = self.pipeline.predict([processed_text])[0]
        
        # Get prediction probabilities
        probabilities = self.pipeline.predict_proba([processed_text])[0]
        confidence = max(probabilities)
        
        return prediction, confidence
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Predict cuisine types for multiple texts"""
        if self.pipeline is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Predict
        predictions = self.pipeline.predict(processed_texts)
        probabilities = self.pipeline.predict_proba(processed_texts)
        
        # Get confidence scores
        confidences = [max(prob) for prob in probabilities]
        
        return list(zip(predictions, confidences))
    
    def classify_restaurants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify restaurants in the dataset using the trained model"""
        if self.pipeline is None:
            print("Model not trained. Using rule-based classification instead.")
            return self._rule_based_classification(df)
        
        print("Classifying restaurants using ML model...")
        
        # Prepare texts for classification
        texts_to_classify = []
        for _, row in df.iterrows():
            text_parts = []
            
            if pd.notna(row.get('name')):
                text_parts.append(str(row['name']))
            
            if pd.notna(row.get('description')):
                text_parts.append(str(row['description']))
            
            combined_text = ' '.join(text_parts)
            texts_to_classify.append(combined_text)
        
        # Predict cuisines
        predictions = self.predict_batch(texts_to_classify)
        
        # Update dataframe
        df_copy = df.copy()
        df_copy['predicted_cuisine'] = [pred[0] for pred in predictions]
        df_copy['classification_confidence'] = [pred[1] for pred in predictions]
        
        # Use predicted cuisine if confidence is high enough, otherwise keep original
        confidence_threshold = 0.6
        df_copy['final_cuisine_type'] = df_copy.apply(
            lambda row: row['predicted_cuisine'] 
            if row['classification_confidence'] > confidence_threshold 
            else row.get('cuisine_type', 'Pakistani'), 
            axis=1
        )
        
        return df_copy
    
    def _rule_based_classification(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fallback rule-based classification"""
        print("Using rule-based classification...")
        
        df_copy = df.copy()
        df_copy['predicted_cuisine'] = 'Pakistani'
        df_copy['classification_confidence'] = 0.5
        df_copy['final_cuisine_type'] = df_copy['cuisine_type'].fillna('Pakistani')
        
        return df_copy
    
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
        """Get feature importance (for Random Forest only)"""
        if self.pipeline is None or self.model_type != 'random_forest':
            return {}
        
        # Get feature names from vectorizer
        vectorizer = self.pipeline.named_steps['tfidf']
        feature_names = vectorizer.get_feature_names_out()
        
        # Get feature importance from classifier
        classifier = self.pipeline.named_steps['classifier']
        importances = classifier.feature_importances_
        
        # Create feature importance dictionary
        feature_importance = dict(zip(feature_names, importances))
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_features[:50])  # Return top 50 features 