"""
Text Processing and Chunking Utilities
Handles document preprocessing, cleaning, and chunking for RAG
"""
from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_doc_id: Optional[str] = None


class TextProcessor:
    """Handles text preprocessing and cleaning"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]', '', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def normalize_text(text: str, lowercase: bool = False) -> str:
        """
        Normalize text

        Args:
            text: Input text
            lowercase: Whether to convert to lowercase

        Returns:
            Normalized text
        """
        if lowercase:
            text = text.lower()

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        # Normalize dashes
        text = text.replace('—', '-').replace('–', '-')

        return text

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)

    @staticmethod
    def remove_emails(text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)


class DocumentChunker:
    """Chunks documents into smaller pieces for better retrieval"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n\n"
    ):
        """
        Initialize document chunker

        Args:
            chunk_size: Target size of each chunk (in characters)
            chunk_overlap: Number of characters to overlap between chunks
            separator: Primary separator for splitting (e.g., paragraphs)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """
        Chunk a single text document

        Args:
            text: Document text
            metadata: Metadata to attach to each chunk

        Returns:
            List of DocumentChunk objects
        """
        if metadata is None:
            metadata = {}

        # Clean the text first
        text = TextProcessor.clean_text(text)

        chunks = []
        current_pos = 0
        chunk_num = 0

        # Split by separator first (e.g., paragraphs)
        paragraphs = text.split(self.separator)

        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunk_metadata = {
                    **metadata,
                    "chunk_num": chunk_num,
                    "chunk_size": len(current_chunk)
                }

                chunks.append(DocumentChunk(
                    text=current_chunk.strip(),
                    metadata=chunk_metadata,
                    chunk_id=f"chunk_{chunk_num}"
                ))

                chunk_num += 1

                # Keep overlap from previous chunk
                if self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + para
                else:
                    current_chunk = para
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += " " + para
                else:
                    current_chunk = para

        # Add the last chunk
        if current_chunk:
            chunk_metadata = {
                **metadata,
                "chunk_num": chunk_num,
                "chunk_size": len(current_chunk)
            }

            chunks.append(DocumentChunk(
                text=current_chunk.strip(),
                metadata=chunk_metadata,
                chunk_id=f"chunk_{chunk_num}"
            ))

        return chunks

    def chunk_by_sentences(
        self,
        text: str,
        max_sentences: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Chunk text by sentences

        Args:
            text: Document text
            max_sentences: Maximum number of sentences per chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of DocumentChunk objects
        """
        if metadata is None:
            metadata = {}

        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        chunk_num = 0

        for i in range(0, len(sentences), max_sentences):
            chunk_sentences = sentences[i:i + max_sentences]
            chunk_text = " ".join(chunk_sentences)

            chunk_metadata = {
                **metadata,
                "chunk_num": chunk_num,
                "sentence_count": len(chunk_sentences)
            }

            chunks.append(DocumentChunk(
                text=chunk_text.strip(),
                metadata=chunk_metadata,
                chunk_id=f"chunk_{chunk_num}"
            ))

            chunk_num += 1

        return chunks

    def chunk_documents(
        self,
        documents: List[Dict[str, Any]],
        text_field: str = "text",
        metadata_fields: Optional[List[str]] = None
    ) -> List[DocumentChunk]:
        """
        Chunk multiple documents

        Args:
            documents: List of document dicts
            text_field: Field name containing the text
            metadata_fields: List of fields to include as metadata

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for doc_idx, doc in enumerate(documents):
            text = doc.get(text_field, "")

            # Extract metadata
            metadata = {"source_doc_idx": doc_idx}
            if metadata_fields:
                for field in metadata_fields:
                    if field in doc:
                        metadata[field] = doc[field]

            # Chunk the document
            chunks = self.chunk_text(text, metadata)

            # Set source document ID for each chunk
            for chunk in chunks:
                chunk.source_doc_id = str(doc_idx)

            all_chunks.extend(chunks)

        return all_chunks


class ContextBuilder:
    """Builds context for prompts from retrieved chunks"""

    @staticmethod
    def build_context(
        chunks: List[DocumentChunk],
        max_context_length: int = 2000,
        include_metadata: bool = True
    ) -> str:
        """
        Build context string from chunks

        Args:
            chunks: List of retrieved chunks
            max_context_length: Maximum length of context
            include_metadata: Whether to include metadata in context

        Returns:
            Context string
        """
        context_parts = []
        current_length = 0

        for i, chunk in enumerate(chunks):
            # Format chunk with metadata
            if include_metadata and chunk.metadata:
                source = chunk.metadata.get("source", "Unknown")
                category = chunk.metadata.get("category", "General")
                chunk_text = f"[Source: {source}, Category: {category}]\n{chunk.text}"
            else:
                chunk_text = chunk.text

            # Check if adding this chunk exceeds max length
            if current_length + len(chunk_text) > max_context_length:
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        # Join with separators
        context = "\n\n---\n\n".join(context_parts)

        return context

    @staticmethod
    def build_structured_context(
        chunks: List[DocumentChunk],
        max_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Build structured context with metadata

        Args:
            chunks: List of retrieved chunks
            max_chunks: Maximum number of chunks to include

        Returns:
            Structured context dict
        """
        limited_chunks = chunks[:max_chunks]

        return {
            "num_chunks": len(limited_chunks),
            "chunks": [
                {
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "chunk_id": chunk.chunk_id
                }
                for chunk in limited_chunks
            ]
        }
