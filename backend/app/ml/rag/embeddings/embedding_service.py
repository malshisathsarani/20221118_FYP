"""
Embedding Service for RAG Pipeline
Handles document and query embeddings using sentence-transformers
"""
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path


class EmbeddingService:
    """Service for generating embeddings for documents and queries"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = None):
        """
        Initialize the embedding service

        Args:
            model_name: Name of the sentence-transformer model to use
                       Default: all-MiniLM-L6-v2 (fast, good quality, 384 dim)
                       Alternatives:
                       - all-mpnet-base-v2 (best quality, 768 dim, slower)
                       - paraphrase-multilingual-MiniLM-L12-v2 (multilingual support)
            cache_dir: Directory to cache the model
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or str(Path(__file__).parent.parent / "pretrained_models")

        # Load the model
        self.model = SentenceTransformer(
            self.model_name,
            cache_folder=self.cache_dir
        )

        # Handle both old and new versions of sentence-transformers
        try:
            self.embedding_dimension = self.model.get_embedding_dimension()
        except AttributeError:
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of documents

        Args:
            documents: List of document texts

        Returns:
            numpy array of shape (n_documents, embedding_dimension)
        """
        if not documents:
            return np.array([])

        embeddings = self.model.encode(
            documents,
            convert_to_numpy=True,
            show_progress_bar=len(documents) > 10,
            batch_size=32
        )

        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query

        Args:
            query: Query text

        Returns:
            numpy array of shape (embedding_dimension,)
        """
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return embedding

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts (generic method)

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding

        Returns:
            numpy array of shape (n_texts, embedding_dimension)
        """
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10,
            batch_size=batch_size
        )

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_dimension

    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": self.model.max_seq_length,
            "cache_dir": self.cache_dir
        }


# Singleton instance for reuse across the application
_embedding_service_instance = None


def get_embedding_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    """
    Get or create a singleton instance of EmbeddingService

    Args:
        model_name: Model name (only used on first call)

    Returns:
        EmbeddingService instance
    """
    global _embedding_service_instance

    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(model_name=model_name)

    return _embedding_service_instance
