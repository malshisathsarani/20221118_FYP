"""Knowledge base module"""
from .sample_mental_health_kb import (
    get_sample_knowledge_base,
    get_documents_by_category,
    get_documents_by_culture,
    get_categories,
    get_cultures,
    ALL_DOCUMENTS
)

__all__ = [
    "get_sample_knowledge_base",
    "get_documents_by_category",
    "get_documents_by_culture",
    "get_categories",
    "get_cultures",
    "ALL_DOCUMENTS"
]
