from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HSNSuggester:
    def __init__(self, data_handler):
        self.data = data_handler
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._train_model()
    
    def _train_model(self):
        """Train suggestion model"""
        descriptions = self.data.data['Description'].tolist()
        self.tfidf_matrix = self.vectorizer.fit_transform(descriptions)
    
    def suggest(self, query, top_k=5):
        """Get HSN suggestions"""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        indices = scores.argsort()[-top_k:][::-1]
        return [{
            'hsn_code': self.data.data.iloc[i]['HSNCode'],
            'description': self.data.data.iloc[i]['Description'],
            'score': float(scores[i])
        } for i in indices]
