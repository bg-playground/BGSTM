"""Similarity algorithms for link suggestion"""

import hashlib
import re
from collections import Counter


def compute_text_hash(text: str) -> str:
    """Return the SHA-256 hex digest of *text* (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SimilarityAlgorithm:
    """Base class for similarity algorithms"""

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts. Returns score 0.0-1.0"""
        raise NotImplementedError

    def precompute_embeddings(self, texts: list[str]) -> None:
        """Pre-compute embeddings for a list of texts. No-op by default."""


class TFIDFSimilarity(SimilarityAlgorithm):
    """TF-IDF based cosine similarity using scikit-learn"""

    def __init__(self, max_features: int = 100, ngram_range: tuple[int, int] = (1, 2)):
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
                max_features=max_features, ngram_range=ngram_range, stop_words="english", lowercase=True
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

    def batch_compute_similarity(self, texts: list[str]) -> list[list[float]]:
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
            "the",
            "be",
            "to",
            "of",
            "and",
            "a",
            "in",
            "that",
            "have",
            "it",
            "for",
            "not",
            "on",
            "with",
            "he",
            "as",
            "you",
            "do",
            "at",
            "this",
            "but",
            "his",
            "by",
            "from",
            "they",
            "we",
            "say",
            "her",
            "she",
            "or",
            "an",
            "will",
            "my",
            "one",
            "all",
            "would",
            "there",
            "their",
            "what",
            "so",
            "up",
            "out",
            "if",
            "about",
            "who",
            "get",
            "which",
            "go",
            "me",
            "when",
            "make",
            "can",
            "like",
            "time",
            "no",
            "just",
            "him",
            "know",
            "take",
            "into",
            "year",
            "your",
            "good",
            "some",
            "could",
            "them",
            "see",
            "other",
            "than",
            "then",
            "now",
            "look",
            "only",
            "come",
            "its",
            "over",
            "think",
            "also",
            "back",
            "after",
            "use",
            "two",
            "how",
            "our",
            "work",
            "first",
            "well",
            "way",
            "even",
            "new",
            "want",
            "because",
            "any",
            "these",
            "give",
            "day",
            "most",
            "us",
            "is",
            "was",
            "are",
            "been",
            "has",
            "had",
            "were",
            "said",
            "did",
            "having",
            "may",
            "should",
            "must",
        }

    def extract_keywords(self, text: str) -> list[str]:
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
        words = re.findall(r"\b[a-z0-9]+\b", text_lower)

        # Filter by length and stop words
        filtered_words = [w for w in words if len(w) >= self.min_word_length and w not in self.stop_words]

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
        tfidf_kwargs: dict | None = None,
        keyword_kwargs: dict | None = None,
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
            return self.tfidf_weight * tfidf_score + self.keyword_weight * keyword_score
        else:
            return keyword_score


class LLMEmbeddingSimilarity(SimilarityAlgorithm):
    """LLM-based embedding similarity using OpenAI or HuggingFace"""

    def __init__(
        self, provider: str = "openai", model: str = None, cache_embeddings: bool = True, batch_size: int = 2048
    ):
        """
        Args:
            provider: 'openai' or 'huggingface'
            model: Model name (e.g., 'text-embedding-3-small' for OpenAI,
                'sentence-transformers/all-MiniLM-L6-v2' for HF)
            cache_embeddings: Whether to cache embeddings in memory for performance
            batch_size: Maximum number of texts per batch embedding API call
        """
        self.provider = provider.lower()
        self.cache_embeddings = cache_embeddings
        self.batch_size = batch_size
        self._embedding_cache = {} if cache_embeddings else None

        if self.provider == "openai":
            self.model = model or "text-embedding-3-small"
            self._init_openai()
        elif self.provider == "huggingface":
            # HuggingFace model: can use short name like 'all-MiniLM-L6-v2'
            # or full path like 'sentence-transformers/all-MiniLM-L6-v2'
            self.model = model or "all-MiniLM-L6-v2"
            self._init_huggingface()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import os

            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

    def _init_huggingface(self):
        """Initialize HuggingFace model"""
        try:
            from sentence_transformers import SentenceTransformer

            self.model_instance = SentenceTransformer(self.model)
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")

    def _get_embedding_openai(self, text: str) -> list[float]:
        """Get embedding from OpenAI"""
        if self.cache_embeddings and self._embedding_cache is not None and text in self._embedding_cache:
            return self._embedding_cache[text]

        response = self.client.embeddings.create(input=text, model=self.model)
        embedding = response.data[0].embedding

        if self.cache_embeddings and self._embedding_cache is not None:
            self._embedding_cache[text] = embedding

        return embedding

    def _get_embedding_huggingface(self, text: str) -> list[float]:
        """Get embedding from HuggingFace"""
        if self.cache_embeddings and self._embedding_cache is not None and text in self._embedding_cache:
            return self._embedding_cache[text]

        embedding = self.model_instance.encode(text).tolist()

        if self.cache_embeddings and self._embedding_cache is not None:
            self._embedding_cache[text] = embedding

        return embedding

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for a batch of texts, using cache where available.

        Uncached texts are sent to the API/model in a single batched call.
        Handles the OpenAI batch size limit (2048) by chunking if needed.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors in the same order as the input texts
        """
        if not texts:
            return []

        # Local result map covers both cached and newly fetched embeddings
        result_map: dict[str, list[float]] = {}

        # Populate from cache first
        if self._embedding_cache is not None:
            for t in texts:
                if t in self._embedding_cache:
                    result_map[t] = self._embedding_cache[t]

        # Collect unique uncached texts (preserve order with dict.fromkeys)
        unique_uncached = list(dict.fromkeys(t for t in texts if t not in result_map))

        if unique_uncached:
            # Chunk to respect API limits (OpenAI max: 2048)
            chunk_size = self.batch_size
            for i in range(0, len(unique_uncached), chunk_size):
                chunk = unique_uncached[i : i + chunk_size]
                if self.provider == "openai":
                    response = self.client.embeddings.create(input=chunk, model=self.model)
                    new_embeddings = [item.embedding for item in response.data]
                else:  # huggingface
                    new_embeddings = [vec.tolist() for vec in self.model_instance.encode(chunk)]

                for text, embedding in zip(chunk, new_embeddings):
                    result_map[text] = embedding
                    if self.cache_embeddings and self._embedding_cache is not None:
                        self._embedding_cache[text] = embedding

        return [result_map[t] for t in texts]

    def precompute_embeddings(self, texts: list[str]) -> None:
        """Pre-compute and cache embeddings for a list of texts in a single batched API call."""
        self.get_embeddings_batch(texts)

    async def load_cached_embeddings(self, db: object, texts: list[str]) -> dict[str, list[float]]:
        """
        Load embeddings from the persistent DB cache into the in-memory cache.

        For each text whose SHA-256 hash is found in the ``embedding_cache`` table,
        the embedding is stored in ``self._embedding_cache`` so that subsequent
        calls to :meth:`precompute_embeddings` / :meth:`get_embeddings_batch` will
        skip the API call entirely.

        Args:
            db: An async SQLAlchemy ``AsyncSession``.
            texts: Texts to look up.

        Returns:
            Mapping of ``text → embedding`` for every cache hit.
        """
        if not texts or self._embedding_cache is None:
            return {}

        try:
            from app.crud.embedding_cache import get_cached_embeddings_batch

            hash_to_text = {compute_text_hash(t): t for t in texts}
            hits = await get_cached_embeddings_batch(db, list(hash_to_text.keys()), self.model)

            result: dict[str, list[float]] = {}
            for text_hash, embedding in hits.items():
                text = hash_to_text[text_hash]
                self._embedding_cache[text] = embedding
                result[text] = embedding
            return result
        except Exception:
            # Gracefully degrade — DB cache unavailable, fall back to in-memory only.
            import logging

            logging.getLogger(__name__).warning("DB embedding cache unavailable; using in-memory cache only.")
            return {}

    async def save_embeddings_to_db(self, db: object, texts: list[str]) -> None:
        """
        Persist embeddings for *texts* that are already in the in-memory cache to the DB.

        Only texts present in ``self._embedding_cache`` are saved — this is called
        after :meth:`precompute_embeddings` so all freshly computed embeddings are
        written through to the persistent store.

        Args:
            db: An async SQLAlchemy ``AsyncSession``.
            texts: Texts whose embeddings should be saved.
        """
        if not texts or self._embedding_cache is None:
            return

        try:
            from app.crud.embedding_cache import save_embeddings_batch

            entries = []
            for text in texts:
                embedding = self._embedding_cache.get(text)
                if embedding is not None:
                    entries.append(
                        {
                            "text_hash": compute_text_hash(text),
                            "embedding": embedding,
                            "model_name": self.model,
                            "provider": self.provider,
                        }
                    )

            await save_embeddings_batch(db, entries)
        except Exception:
            import logging

            logging.getLogger(__name__).warning("Failed to persist embeddings to DB cache; continuing without save.")

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute similarity using LLM embeddings

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1.strip() or not text2.strip():
            return 0.0

        try:
            if self.provider == "openai":
                emb1 = self._get_embedding_openai(text1)
                emb2 = self._get_embedding_openai(text2)
            else:  # huggingface
                emb1 = self._get_embedding_huggingface(text1)
                emb2 = self._get_embedding_huggingface(text2)

            # Cosine similarity returns -1 to 1, normalize to 0 to 1
            similarity = self._cosine_similarity(emb1, emb2)
            return (similarity + 1.0) / 2.0

        except Exception as e:
            # Log error and return 0 to avoid breaking the entire generation process
            import logging

            logging.error(f"Error computing LLM similarity: {e}")
            return 0.0


def get_algorithm(algorithm_name: str, config=None) -> SimilarityAlgorithm:
    """
    Factory function to get a similarity algorithm by name

    Args:
        algorithm_name: Name of the algorithm ('tfidf', 'keyword', 'hybrid', or 'llm')
        config: Optional SuggestionConfig object

    Returns:
        SimilarityAlgorithm instance
    """
    algorithm_name = algorithm_name.lower()

    if algorithm_name == "llm":
        kwargs = {}
        if config:
            kwargs = {
                "provider": getattr(config, "llm_provider", "openai"),
                "model": getattr(config, "llm_model", None),
                "cache_embeddings": getattr(config, "llm_cache_embeddings", True),
                "batch_size": getattr(config, "llm_batch_size", 2048),
            }
        return LLMEmbeddingSimilarity(**kwargs)

    elif algorithm_name == "tfidf":
        kwargs = {}
        if config:
            kwargs = {"max_features": config.tfidf_max_features, "ngram_range": config.tfidf_ngram_range}
        return TFIDFSimilarity(**kwargs)

    elif algorithm_name == "keyword":
        kwargs = {}
        if config:
            kwargs = {"min_word_length": config.keyword_min_word_length, "top_n": config.keyword_top_n}
        return KeywordSimilarity(**kwargs)

    elif algorithm_name == "hybrid":
        tfidf_kwargs = {}
        keyword_kwargs = {}
        hybrid_kwargs = {}

        if config:
            tfidf_kwargs = {"max_features": config.tfidf_max_features, "ngram_range": config.tfidf_ngram_range}
            keyword_kwargs = {"min_word_length": config.keyword_min_word_length, "top_n": config.keyword_top_n}
            hybrid_kwargs = {"tfidf_weight": config.hybrid_tfidf_weight, "keyword_weight": config.hybrid_keyword_weight}

        return HybridSimilarity(tfidf_kwargs=tfidf_kwargs, keyword_kwargs=keyword_kwargs, **hybrid_kwargs)

    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
