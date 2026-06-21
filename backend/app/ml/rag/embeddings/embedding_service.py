"""
Embedding Service for RAG Pipeline
Handles document and query embeddings using sentence-transformers
"""
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import os

# Disable HuggingFace Hub telemetry and force offline mode
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'


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

        # Load the model from local cache (no network calls)
        import os
        import logging
        logger = logging.getLogger(__name__)

        # Path to local cached model
        local_model_path = os.path.join(
            self.cache_dir,
            f"models--sentence-transformers--{self.model_name}",
            "snapshots",
            "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"  # Snapshot hash
        )

        try:
            if os.path.exists(local_model_path):
                # Load from local path directly (no HuggingFace network call)
                logger.info(f"Loading sentence-transformer from local cache: {local_model_path}")
                self.model = SentenceTransformer(local_model_path, device='cpu')
                logger.info("✓ Sentence-transformer loaded successfully from cache")
            else:
                # Fallback to downloading (with local_files_only to prevent network errors)
                logger.warning(f"Local model not found at {local_model_path}, attempting download...")
                self.model = SentenceTransformer(
                    self.model_name,
                    cache_folder=self.cache_dir,
                    device='cpu'
                )
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer: {e}")
            raise

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
