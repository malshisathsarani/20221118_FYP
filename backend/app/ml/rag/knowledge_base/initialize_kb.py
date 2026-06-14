"""
Script to initialize the knowledge base with sample documents
Run this to populate the vector store with mental health content
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.ml.rag import get_rag_pipeline
from app.ml.rag.knowledge_base import get_sample_knowledge_base


def initialize_knowledge_base(reset: bool = False):
    """
    Initialize the knowledge base with sample documents

    Args:
        reset: If True, delete existing documents first
    """
    print("Initializing RAG Pipeline...")
    pipeline = get_rag_pipeline()

    if reset:
        print("Resetting knowledge base...")
        try:
            pipeline.delete_all()
            print("Knowledge base reset complete")
            # Recreate pipeline after deletion
            pipeline = get_rag_pipeline()
        except Exception as e:
            print(f"Error resetting knowledge base: {e}")

    print("\nLoading sample documents...")
    documents = get_sample_knowledge_base()
    print(f"Found {len(documents)} documents")

    print("\nAdding documents to knowledge base...")
    result = pipeline.add_documents(
        documents=documents,
        text_field="text",
        metadata_fields=["category", "source", "culture", "topic"]
    )

    print(f"\n✓ Successfully added documents:")
    print(f"  - Total documents: {result['num_documents']}")
    print(f"  - Total chunks: {result['num_chunks']}")
    print(f"  - Average chunks per document: {result['num_chunks'] / result['num_documents']:.1f}")

    # Get stats
    stats = pipeline.get_stats()
    print(f"\nKnowledge Base Statistics:")
    print(f"  - Collection: {stats['collection_name']}")
    print(f"  - Total chunks in DB: {stats['num_documents']}")
    print(f"  - Embedding model: {stats['embedding_model']['model_name']}")
    print(f"  - Embedding dimension: {stats['embedding_model']['embedding_dimension']}")

    print("\n✓ Knowledge base initialization complete!")

    return pipeline


def test_retrieval(pipeline):
    """Test retrieval with sample queries"""
    test_queries = [
        "How can I manage my anxiety?",
        "I'm feeling depressed and don't know what to do",
        "What are some culturally sensitive approaches for Asian families?",
        "I'm having thoughts of suicide",
        "How can I help someone in crisis?"
    ]

    print("\n" + "="*60)
    print("Testing Retrieval with Sample Queries")
    print("="*60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)

        response = pipeline.query(
            query=query,
            top_k=3,
            include_metadata=True
        )

        print(f"Retrieved {response.metadata['num_retrieved']} documents")
        print(f"Average relevance score: {response.metadata['avg_score']:.3f}")

        for i, doc in enumerate(response.retrieved_docs, 1):
            category = doc.metadata.get('category', 'N/A')
            culture = doc.metadata.get('culture', 'N/A')
            print(f"\n  {i}. [Score: {doc.score:.3f}] Category: {category}, Culture: {culture}")
            print(f"     {doc.text[:150]}...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize RAG knowledge base")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset knowledge base before initialization"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test queries after initialization"
    )

    args = parser.parse_args()

    try:
        pipeline = initialize_knowledge_base(reset=args.reset)

        if args.test:
            test_retrieval(pipeline)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
