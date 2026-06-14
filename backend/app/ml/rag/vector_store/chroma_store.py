"""
ChromaDB Vector Store Service
Manages document storage and retrieval using ChromaDB
"""
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import uuid
from pathlib import Path


class ChromaVectorStore:
    """Vector store using ChromaDB for document storage and retrieval"""

    def __init__(
        self,
        collection_name: str = "mental_health_docs",
        persist_directory: str = None,
        embedding_function=None
    ):
        """
        Initialize ChromaDB vector store

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            embedding_function: Custom embedding function (optional)
        """
        self.collection_name = collection_name

        # Set persist directory
        if persist_directory is None:
            persist_directory = str(
                Path(__file__).parent.parent.parent.parent / "data" / "chroma_db"
            )

        self.persist_directory = persist_directory

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Mental health knowledge base for RAG"}
        )

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts for each document
            ids: List of document IDs (generated if not provided)

        Returns:
            List of document IDs
        """
        if not documents:
            return []

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

        # Prepare metadatas
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where: Metadata filter (e.g., {"category": "cbt"})
            where_document: Document content filter

        Returns:
            Dict containing ids, documents, metadatas, and distances
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            where_document=where_document
        )

        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document data or None if not found
        """
        try:
            results = self.collection.get(ids=[doc_id])
            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "document": results["documents"][0],
                    "metadata": results["metadatas"][0]
                }
        except Exception:
            pass

        return None

    def update_document(
        self,
        doc_id: str,
        document: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a document

        Args:
            doc_id: Document ID
            document: New document text
            embedding: New embedding
            metadata: New metadata

        Returns:
            True if successful
        """
        try:
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding] if embedding else None,
                documents=[document] if document else None,
                metadatas=[metadata] if metadata else None
            )
            return True
        except Exception:
            return False

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def delete_collection(self):
        """Delete the entire collection and recreate it"""
        self.client.delete_collection(name=self.collection_name)
        # Recreate the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Mental health knowledge base for RAG"}
        )

    def count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()

    def get_all_documents(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all documents in the collection

        Args:
            limit: Maximum number of documents to retrieve

        Returns:
            Dict containing all documents
        """
        results = self.collection.get(limit=limit)
        return {
            "ids": results["ids"],
            "documents": results["documents"],
            "metadatas": results["metadatas"]
        }

    def peek(self, limit: int = 10) -> Dict[str, Any]:
        """
        Peek at the first few documents

        Args:
            limit: Number of documents to peek

        Returns:
            Dict containing sample documents
        """
        return self.collection.peek(limit=limit)

    def reset(self):
        """Reset the entire database (use with caution!)"""
        self.client.reset()


# Singleton instance
_vector_store_instance = None


def get_vector_store(collection_name: str = "mental_health_docs") -> ChromaVectorStore:
    """
    Get or create a singleton instance of ChromaVectorStore

    Args:
        collection_name: Collection name (only used on first call)

    Returns:
        ChromaVectorStore instance
    """
    global _vector_store_instance

    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore(collection_name=collection_name)

    return _vector_store_instance
