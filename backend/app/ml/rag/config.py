"""
RAG Configuration
Centralized configuration for RAG pipeline
"""
from pydantic import BaseModel
from typing import Optional
from pathlib import Path


class RAGConfig(BaseModel):
    """Configuration for RAG pipeline"""

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: Optional[str] = None

    # Vector store settings
    collection_name: str = "mental_health_docs"
    persist_directory: Optional[str] = None

    # Document chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    chunk_separator: str = "\n\n"

    # Retrieval settings
    top_k: int = 5
    score_threshold: Optional[float] = None
    use_diversity: bool = True
    diversity_weight: float = 0.3
    retriever_type: str = "semantic"  # "semantic" or "hybrid"

    # Context building settings
    max_context_length: int = 1500
    include_metadata: bool = True

    # Performance settings
    batch_size: int = 32
    enable_caching: bool = True

    class Config:
        env_prefix = "RAG_"


# Default configuration instance
default_config = RAGConfig()


def get_config() -> RAGConfig:
    """Get RAG configuration"""
    return default_config


def update_config(**kwargs):
    """Update RAG configuration"""
    global default_config
    for key, value in kwargs.items():
        if hasattr(default_config, key):
            setattr(default_config, key, value)


# Configuration presets for different use cases
PRESETS = {
    "fast": RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        top_k=3,
        chunk_size=300,
        max_context_length=1000,
        use_diversity=False
    ),
    "balanced": RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        top_k=5,
        chunk_size=500,
        max_context_length=1500,
        use_diversity=True,
        diversity_weight=0.3
    ),
    "quality": RAGConfig(
        embedding_model="all-mpnet-base-v2",
        top_k=7,
        chunk_size=600,
        max_context_length=2000,
        use_diversity=True,
        diversity_weight=0.4
    ),
    "multilingual": RAGConfig(
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        top_k=5,
        chunk_size=500,
        max_context_length=1500
    )
}


def load_preset(preset_name: str):
    """Load a configuration preset"""
    global default_config
    if preset_name in PRESETS:
        default_config = PRESETS[preset_name]
    else:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
