"""Similarity algorithms for link suggestion"""

import re
from typing import List, Tuple, Dict
from collections import Counter


class SimilarityAlgorithm:
    """Base class for similarity algorithms"""
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts. Returns score 0.0-1.0"""
        raise NotImplementedError


class TFIDFSimilarity(SimilarityAlgorithm):
    """TF-IDF based cosine similarity using scikit-learn"""
    
    def __init__(self, max_features: int = 100, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize TF-IDF vectorizer
        
        Args:
            max_features: Maximum number of features for TF-IDF
            ngram_range: N-gram range (min, max) for tokenization
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            self.vectorizer = TfidfVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                stop_words='english',
                lowercase=True
            )
            self.cosine_similarity = cosine_similarity
            self._sklearn_available = True
        except ImportError:
            self._sklearn_available = False
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute TF-IDF cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not self._sklearn_available:
            raise ImportError("scikit-learn is required for TF-IDF similarity")
        
        if not text1 or not text2:
            return 0.0
        
        try:
            # Fit and transform both texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity = self.cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception:
            # If vectorization fails (e.g., no valid tokens), return 0
            return 0.0
    
    def batch_compute_similarity(self, texts: List[str]) -> List[List[float]]:
        """
        Compute pairwise similarities for a batch of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Matrix of similarity scores
        """
        if not self._sklearn_available:
            raise ImportError("scikit-learn is required for TF-IDF similarity")
        
        if not texts:
            return []
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity_matrix = self.cosine_similarity(tfidf_matrix, tfidf_matrix)
            return similarity_matrix.tolist()
        except Exception:
            # Return zero matrix if vectorization fails
            n = len(texts)
            return [[0.0] * n for _ in range(n)]


class KeywordSimilarity(SimilarityAlgorithm):
    """Keyword-based heuristic similarity matching"""
    
    def __init__(self, min_word_length: int = 3, top_n: int = 10):
        """
        Initialize keyword matcher
        
        Args:
            min_word_length: Minimum length of words to consider
            top_n: Number of top keywords to extract
        """
        self.min_word_length = min_word_length
        self.top_n = top_n
        
        # Common stop words (basic set)
        self.stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it',
            'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this',
            'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or',
            'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its',
            'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our',
            'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
            'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been',
            'has', 'had', 'were', 'said', 'did', 'having', 'may', 'should', 'must'
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Convert to lowercase and extract words
        text_lower = text.lower()
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z0-9]+\b', text_lower)
        
        # Filter by length and stop words
        filtered_words = [
            w for w in words 
            if len(w) >= self.min_word_length and w not in self.stop_words
        ]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Get top N most common
        top_words = [word for word, _ in word_freq.most_common(self.top_n)]
        
        return top_words
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute keyword-based similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0 based on keyword overlap
        """
        if not text1 or not text2:
            return 0.0
        
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        if union == 0:
            return 0.0
        
        return intersection / union


class HybridSimilarity(SimilarityAlgorithm):
    """Hybrid approach combining multiple algorithms"""
    
    def __init__(
        self,
        tfidf_weight: float = 0.6,
        keyword_weight: float = 0.4,
        tfidf_kwargs: Dict = None,
        keyword_kwargs: Dict = None
    ):
        """
        Initialize hybrid algorithm
        
        Args:
            tfidf_weight: Weight for TF-IDF score
            keyword_weight: Weight for keyword score
            tfidf_kwargs: Arguments for TF-IDF algorithm
            keyword_kwargs: Arguments for keyword algorithm
        """
        self.tfidf_weight = tfidf_weight
        self.keyword_weight = keyword_weight
        
        tfidf_kwargs = tfidf_kwargs or {}
        keyword_kwargs = keyword_kwargs or {}
        
        try:
            self.tfidf_algo = TFIDFSimilarity(**tfidf_kwargs)
            self.use_tfidf = True
        except ImportError:
            # Fall back to keyword-only if sklearn not available
            self.use_tfidf = False
            self.keyword_weight = 1.0
            self.tfidf_weight = 0.0
        
        self.keyword_algo = KeywordSimilarity(**keyword_kwargs)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute hybrid similarity combining TF-IDF and keyword matching
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Weighted similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        keyword_score = self.keyword_algo.compute_similarity(text1, text2)
        
        if self.use_tfidf:
            tfidf_score = self.tfidf_algo.compute_similarity(text1, text2)
            return (self.tfidf_weight * tfidf_score + 
                    self.keyword_weight * keyword_score)
        else:
            return keyword_score


def get_algorithm(algorithm_name: str, config=None) -> SimilarityAlgorithm:
    """
    Factory function to get a similarity algorithm by name
    
    Args:
        algorithm_name: Name of the algorithm ('tfidf', 'keyword', or 'hybrid')
        config: Optional SuggestionConfig object
        
    Returns:
        SimilarityAlgorithm instance
    """
    algorithm_name = algorithm_name.lower()
    
    if algorithm_name == "tfidf":
        kwargs = {}
        if config:
            kwargs = {
                'max_features': config.tfidf_max_features,
                'ngram_range': config.tfidf_ngram_range
            }
        return TFIDFSimilarity(**kwargs)
    
    elif algorithm_name == "keyword":
        kwargs = {}
        if config:
            kwargs = {
                'min_word_length': config.keyword_min_word_length,
                'top_n': config.keyword_top_n
            }
        return KeywordSimilarity(**kwargs)
    
    elif algorithm_name == "hybrid":
        tfidf_kwargs = {}
        keyword_kwargs = {}
        hybrid_kwargs = {}
        
        if config:
            tfidf_kwargs = {
                'max_features': config.tfidf_max_features,
                'ngram_range': config.tfidf_ngram_range
            }
            keyword_kwargs = {
                'min_word_length': config.keyword_min_word_length,
                'top_n': config.keyword_top_n
            }
            hybrid_kwargs = {
                'tfidf_weight': config.hybrid_tfidf_weight,
                'keyword_weight': config.hybrid_keyword_weight
            }
        
        return HybridSimilarity(
            tfidf_kwargs=tfidf_kwargs,
            keyword_kwargs=keyword_kwargs,
            **hybrid_kwargs
        )
    
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
