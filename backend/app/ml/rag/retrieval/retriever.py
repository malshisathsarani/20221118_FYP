"""
Retrieval Service for Semantic Search
Handles document retrieval and ranking
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class RetrievalResult:
    """Represents a retrieved document with relevance score"""
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    score: float  # Similarity/relevance score (lower distance = higher relevance for L2)
    rank: int


class SemanticRetriever:
    """Handles semantic retrieval from vector store"""

    def __init__(self, vector_store, embedding_service):
        """
        Initialize retriever

        Args:
            vector_store: Vector store instance
            embedding_service: Embedding service instance
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query

        Args:
            query: User query
            top_k: Number of documents to retrieve
            metadata_filter: Filter by metadata (e.g., {"category": "cbt"})
            score_threshold: Minimum relevance score (for distance: lower is better)

        Returns:
            List of RetrievalResult objects
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Search vector store
        search_results = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
            where=metadata_filter
        )

        # Convert to RetrievalResult objects
        results = []
        for rank, (doc_id, text, metadata, distance) in enumerate(zip(
            search_results["ids"],
            search_results["documents"],
            search_results["metadatas"],
            search_results["distances"]
        )):
            # Convert distance to similarity score (0-1 range)
            # For L2 distance, we use 1 / (1 + distance)
            similarity_score = 1.0 / (1.0 + distance)

            # Apply score threshold if specified
            if score_threshold is not None and similarity_score < score_threshold:
                continue

            results.append(RetrievalResult(
                doc_id=doc_id,
                text=text,
                metadata=metadata,
                score=similarity_score,
                rank=rank
            ))

        return results

    def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = 5,
        initial_k: int = 20,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve with two-stage retrieval and reranking

        Args:
            query: User query
            top_k: Final number of documents to return
            initial_k: Number of documents to retrieve before reranking
            metadata_filter: Filter by metadata

        Returns:
            List of reranked RetrievalResult objects
        """
        # First stage: retrieve more candidates
        candidates = self.retrieve(
            query=query,
            top_k=initial_k,
            metadata_filter=metadata_filter
        )

        # Second stage: rerank by computing more sophisticated similarity
        # For now, we just return top_k from candidates
        # In future, can add cross-encoder reranking here
        return candidates[:top_k]

    def retrieve_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve documents from a specific category

        Args:
            query: User query
            category: Category to filter by
            top_k: Number of documents to retrieve

        Returns:
            List of RetrievalResult objects
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter={"category": category}
        )

    def retrieve_diverse(
        self,
        query: str,
        top_k: int = 5,
        diversity_weight: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Retrieve diverse documents using MMR (Maximal Marginal Relevance)

        Args:
            query: User query
            top_k: Number of documents to retrieve
            diversity_weight: Weight for diversity (0-1, higher = more diverse)

        Returns:
            List of diverse RetrievalResult objects
        """
        # Retrieve initial candidates (more than needed)
        candidates = self.retrieve(query=query, top_k=top_k * 3)

        if len(candidates) <= top_k:
            return candidates

        # Get embeddings for all candidate documents
        candidate_texts = [r.text for r in candidates]
        candidate_embeddings = self.embedding_service.embed_documents(candidate_texts)

        # Query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # MMR algorithm
        selected_indices = []
        remaining_indices = list(range(len(candidates)))

        for _ in range(min(top_k, len(candidates))):
            best_score = -float('inf')
            best_idx = None

            for idx in remaining_indices:
                # Relevance to query
                relevance = self._cosine_similarity(
                    query_embedding,
                    candidate_embeddings[idx]
                )

                # Diversity: negative similarity to already selected docs
                if selected_indices:
                    max_similarity = max([
                        self._cosine_similarity(
                            candidate_embeddings[idx],
                            candidate_embeddings[sel_idx]
                        )
                        for sel_idx in selected_indices
                    ])
                    diversity = -max_similarity
                else:
                    diversity = 0

                # MMR score
                mmr_score = (1 - diversity_weight) * relevance + diversity_weight * diversity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx is not None:
                selected_indices.append(best_idx)
                remaining_indices.remove(best_idx)

        # Return selected results with updated ranks
        diverse_results = [candidates[idx] for idx in selected_indices]
        for rank, result in enumerate(diverse_results):
            result.rank = rank

        return diverse_results

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


class HybridRetriever:
    """Combines semantic and keyword-based retrieval"""

    def __init__(self, semantic_retriever: SemanticRetriever):
        """
        Initialize hybrid retriever

        Args:
            semantic_retriever: Semantic retriever instance
        """
        self.semantic_retriever = semantic_retriever

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7
    ) -> List[RetrievalResult]:
        """
        Hybrid retrieval combining semantic and keyword search

        Args:
            query: User query
            top_k: Number of documents to retrieve
            semantic_weight: Weight for semantic search (0-1)

        Returns:
            List of RetrievalResult objects
        """
        # For now, just use semantic retrieval
        # In future, can add BM25 or other keyword-based methods
        return self.semantic_retriever.retrieve(query=query, top_k=top_k)


# Factory function
def create_retriever(vector_store, embedding_service, retriever_type: str = "semantic"):
    """
    Create a retriever instance

    Args:
        vector_store: Vector store instance
        embedding_service: Embedding service instance
        retriever_type: Type of retriever ("semantic" or "hybrid")

    Returns:
        Retriever instance
    """
    semantic_retriever = SemanticRetriever(vector_store, embedding_service)

    if retriever_type == "hybrid":
        return HybridRetriever(semantic_retriever)

    return semantic_retriever
