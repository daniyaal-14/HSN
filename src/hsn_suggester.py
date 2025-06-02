# src/hsn_suggester.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from .data_handler import HSNDataHandler

class HSNSuggester:
    """ML-based HSN code suggestion system using TF-IDF and cosine similarity"""
    
    def __init__(self, data_handler: HSNDataHandler):
        """
        Initialize suggester with data handler
        
        Args:
            data_handler (HSNDataHandler): Instance of HSN data handler
        """
        self.data_handler = data_handler
        self.vectorizer = None
        self.description_vectors = None
        self.descriptions = None
        self.min_similarity_threshold = 0.1
        self._prepare_vectors()
    
    def _prepare_vectors(self):
        """Prepare TF-IDF vectors for all HSN descriptions"""
        try:
            print("Preparing TF-IDF vectors for HSN suggestions...")
            
            # Get all descriptions
            self.descriptions = self.data_handler.hsn_data['Description'].tolist()
            
            # Initialize TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=5000,
                ngram_range=(1, 2),  # Use both unigrams and bigrams
                min_df=1,  # Minimum document frequency
                max_df=0.95,  # Maximum document frequency
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Fit and transform descriptions
            self.description_vectors = self.vectorizer.fit_transform(self.descriptions)
            
            print(f"TF-IDF vectors prepared successfully!")
            print(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
            print(f"Vector shape: {self.description_vectors.shape}")
            
        except Exception as e:
            raise Exception(f"Error preparing TF-IDF vectors: {str(e)}")
    
    def suggest_hsn_codes(self, product_description: str, top_k: int = 5) -> List[Dict]:
        """
        Suggest HSN codes based on product description using ML similarity
        
        Args:
            product_description (str): Description of the product
            top_k (int): Number of suggestions to return
            
        Returns:
            List of HSN code suggestions with similarity scores
        """
        if not product_description or not product_description.strip():
            return []
        
        try:
            # Vectorize the input description
            query_vector = self.vectorizer.transform([product_description.strip()])
            
            # Calculate cosine similarity with all descriptions
            similarities = cosine_similarity(query_vector, self.description_vectors).flatten()
            
            # Get top-k most similar descriptions
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Get more to filter
            
            suggestions = []
            seen_codes = set()  # Avoid duplicate codes
            
            for idx in top_indices:
                similarity_score = similarities[idx]
                
                # Only include if similarity is above threshold
                if similarity_score >= self.min_similarity_threshold:
                    row = self.data_handler.hsn_data.iloc[idx]
                    hsn_code = row['HSNCode']
                    
                    # Avoid duplicates
                    if hsn_code not in seen_codes:
                        suggestions.append({
                            'hsn_code': hsn_code,
                            'description': row['Description'],
                            'similarity_score': float(similarity_score),
                            'confidence_level': self._get_confidence_level(similarity_score),
                            'match_type': 'ml_similarity'
                        })
                        seen_codes.add(hsn_code)
                        
                        # Stop when we have enough suggestions
                        if len(suggestions) >= top_k:
                            break
            
            # If no good ML matches, try keyword-based search
            if len(suggestions) < top_k:
                keyword_suggestions = self._keyword_based_search(product_description, top_k - len(suggestions))
                
                # Add keyword suggestions that aren't already included
                for suggestion in keyword_suggestions:
                    if suggestion['hsn_code'] not in seen_codes:
                        suggestions.append(suggestion)
            
            return suggestions[:top_k]
            
        except Exception as e:
            print(f"Error in ML-based suggestion: {str(e)}")
            # Fallback to keyword search
            return self._keyword_based_search(product_description, top_k)
    
    def _get_confidence_level(self, similarity_score: float) -> str:
        """
        Convert similarity score to confidence level
        
        Args:
            similarity_score (float): Cosine similarity score
            
        Returns:
            str: Confidence level description
        """
        if similarity_score >= 0.7:
            return "High"
        elif similarity_score >= 0.4:
            return "Medium"
        elif similarity_score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def _keyword_based_search(self, product_description: str, limit: int) -> List[Dict]:
        """
        Fallback keyword-based search when ML similarity is low
        
        Args:
            product_description (str): Product description
            limit (int): Maximum number of results
            
        Returns:
            List of HSN code suggestions
        """
        # Extract keywords from product description
        keywords = product_description.lower().split()
        
        suggestions = []
        seen_codes = set()
        
        for keyword in keywords:
            if len(keyword) > 2:  # Skip very short words
                keyword_results = self.data_handler.search_by_description(keyword, limit * 2)
                
                for result in keyword_results:
                    if result['hsn_code'] not in seen_codes:
                        result['similarity_score'] = 0.1  # Low score for keyword matches
                        result['confidence_level'] = 'Low'
                        result['match_type'] = 'keyword_search'
                        suggestions.append(result)
                        seen_codes.add(result['hsn_code'])
                        
                        if len(suggestions) >= limit:
                            break
                
                if len(suggestions) >= limit:
                    break
        
        return suggestions[:limit]
    
    def suggest_with_explanation(self, product_description: str, top_k: int = 5) -> Dict:
        """
        Suggest HSN codes with detailed explanation of the matching process
        
        Args:
            product_description (str): Product description
            top_k (int): Number of suggestions
            
        Returns:
            Dict with suggestions and explanation
        """
        suggestions = self.suggest_hsn_codes(product_description, top_k)
        
        # Analyze the input
        query_vector = self.vectorizer.transform([product_description])
        feature_names = self.vectorizer.get_feature_names_out()
        query_features = query_vector.toarray()[0]
        
        # Get top features from the query
        top_feature_indices = np.argsort(query_features)[::-1][:10]
        top_features = [feature_names[i] for i in top_feature_indices if query_features[i] > 0]
        
        return {
            'query': product_description,
            'suggestions': suggestions,
            'analysis': {
                'key_terms_identified': top_features,
                'total_suggestions': len(suggestions),
                'suggestion_methods': list(set([s['match_type'] for s in suggestions]))
            }
        }
    
    def update_similarity_threshold(self, new_threshold: float):
        """
        Update the minimum similarity threshold
        
        Args:
            new_threshold (float): New threshold value (0.0 to 1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            self.min_similarity_threshold = new_threshold
            print(f"Similarity threshold updated to: {new_threshold}")
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
