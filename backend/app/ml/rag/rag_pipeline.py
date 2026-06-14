"""
RAG Pipeline Orchestrator
Main interface for the RAG system
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from .embeddings import get_embedding_service, EmbeddingService
from .vector_store import get_vector_store, ChromaVectorStore
from .retrieval import create_retriever, RetrievalResult
from .utils import DocumentChunker, ContextBuilder, DocumentChunk, TextProcessor

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Response from RAG pipeline"""
    query: str
    retrieved_docs: List[RetrievalResult]
    context: str
    metadata: Dict[str, Any]


class RAGPipeline:
    """Main RAG pipeline orchestrator"""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "mental_health_docs",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        retriever_type: str = "semantic"
    ):
        """
        Initialize RAG pipeline

        Args:
            embedding_model: Name of the embedding model
            collection_name: Name of the vector store collection
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
            retriever_type: Type of retriever ("semantic" or "hybrid")
        """
        # Initialize components
        self.embedding_service = get_embedding_service(model_name=embedding_model)
        self.vector_store = get_vector_store(collection_name=collection_name)
        self.retriever = create_retriever(
            self.vector_store,
            self.embedding_service,
            retriever_type=retriever_type
        )

        # Initialize utilities
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.context_builder = ContextBuilder()

        logger.info(f"RAG Pipeline initialized with {embedding_model}")

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "text",
        metadata_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to the knowledge base

        Args:
            documents: List of document dicts
            text_field: Field name containing the text
            metadata_fields: Fields to include as metadata

        Returns:
            Dict with ingestion stats
        """
        logger.info(f"Adding {len(documents)} documents to knowledge base")

        # Chunk documents
        chunks = self.chunker.chunk_documents(
            documents,
            text_field=text_field,
            metadata_fields=metadata_fields
        )

        if not chunks:
            logger.warning("No chunks generated from documents")
            return {"num_chunks": 0, "num_documents": 0}

        # Generate embeddings for chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed_documents(chunk_texts)

        # Prepare metadata
        metadatas = [chunk.metadata for chunk in chunks]

        # Add to vector store
        chunk_ids = self.vector_store.add_documents(
            documents=chunk_texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        logger.info(f"Added {len(chunks)} chunks from {len(documents)} documents")

        return {
            "num_documents": len(documents),
            "num_chunks": len(chunks),
            "chunk_ids": chunk_ids
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        use_diversity: bool = False,
        diversity_weight: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query

        Args:
            query: User query
            top_k: Number of documents to retrieve
            metadata_filter: Filter by metadata
            use_diversity: Whether to use diverse retrieval
            diversity_weight: Weight for diversity

        Returns:
            List of RetrievalResult objects
        """
        if use_diversity:
            return self.retriever.retrieve_diverse(
                query=query,
                top_k=top_k,
                diversity_weight=diversity_weight
            )

        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter
        )

    def query(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        max_context_length: int = 2000,
        include_metadata: bool = True,
        use_diversity: bool = False
    ) -> RAGResponse:
        """
        Query the RAG system

        Args:
            query: User query
            top_k: Number of documents to retrieve
            metadata_filter: Filter by metadata
            max_context_length: Maximum context length
            include_metadata: Include metadata in context
            use_diversity: Use diverse retrieval

        Returns:
            RAGResponse object
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
            use_diversity=use_diversity
        )

        # Convert to DocumentChunk format for context building
        chunks = [
            DocumentChunk(
                text=doc.text,
                metadata=doc.metadata,
                chunk_id=doc.doc_id
            )
            for doc in retrieved_docs
        ]

        # Build context
        context = self.context_builder.build_context(
            chunks=chunks,
            max_context_length=max_context_length,
            include_metadata=include_metadata
        )

        # Prepare metadata
        metadata = {
            "num_retrieved": len(retrieved_docs),
            "avg_score": sum(doc.score for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0,
            "sources": [
                {
                    "doc_id": doc.doc_id,
                    "score": doc.score,
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ]
        }

        return RAGResponse(
            query=query,
            retrieved_docs=retrieved_docs,
            context=context,
            metadata=metadata
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        count = self.vector_store.count()

        return {
            "num_documents": count,
            "embedding_model": self.embedding_service.get_model_info(),
            "collection_name": self.vector_store.collection_name
        }

    def delete_all(self):
        """Delete all documents from the knowledge base"""
        logger.warning("Deleting all documents from knowledge base")
        self.vector_store.delete_collection()


class RAGManager:
    """Manager for multiple RAG pipelines (if needed)"""

    def __init__(self):
        self._pipelines: Dict[str, RAGPipeline] = {}

    def create_pipeline(
        self,
        name: str,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: Optional[str] = None
    ) -> RAGPipeline:
        """
        Create a new RAG pipeline

        Args:
            name: Pipeline name
            embedding_model: Embedding model to use
            collection_name: Collection name (defaults to name)

        Returns:
            RAGPipeline instance
        """
        if collection_name is None:
            collection_name = name

        pipeline = RAGPipeline(
            embedding_model=embedding_model,
            collection_name=collection_name
        )

        self._pipelines[name] = pipeline
        return pipeline

    def get_pipeline(self, name: str) -> Optional[RAGPipeline]:
        """Get a pipeline by name"""
        return self._pipelines.get(name)

    def list_pipelines(self) -> List[str]:
        """List all pipeline names"""
        return list(self._pipelines.keys())


# Singleton instance
_rag_pipeline_instance = None


def get_rag_pipeline(
    embedding_model: str = "all-MiniLM-L6-v2",
    collection_name: str = "mental_health_docs"
) -> RAGPipeline:
    """
    Get or create singleton RAG pipeline instance

    Args:
        embedding_model: Embedding model (only used on first call)
        collection_name: Collection name (only used on first call)

    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline_instance

    if _rag_pipeline_instance is None:
        _rag_pipeline_instance = RAGPipeline(
            embedding_model=embedding_model,
            collection_name=collection_name
        )

    return _rag_pipeline_instance
