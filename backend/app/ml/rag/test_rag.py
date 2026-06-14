"""
Comprehensive RAG Pipeline Test Script
Tests all components of the RAG system
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))


def test_embedding_service():
    """Test embedding service"""
    print("\n" + "="*60)
    print("TEST 1: Embedding Service")
    print("="*60)

    from app.ml.rag.embeddings import get_embedding_service

    try:
        service = get_embedding_service()
        print(f"✓ Embedding service initialized")
        print(f"  Model: {service.model_name}")
        print(f"  Dimension: {service.embedding_dimension}")

        # Test single query embedding
        query = "How can I manage my anxiety?"
        embedding = service.embed_query(query)
        print(f"\n✓ Query embedding generated")
        print(f"  Shape: {embedding.shape}")
        print(f"  First 5 values: {embedding[:5]}")

        # Test batch embeddings
        docs = [
            "Cognitive behavioral therapy is effective for anxiety.",
            "Mindfulness meditation can reduce stress.",
            "Regular exercise improves mental health."
        ]
        embeddings = service.embed_documents(docs)
        print(f"\n✓ Document embeddings generated")
        print(f"  Shape: {embeddings.shape}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store"""
    print("\n" + "="*60)
    print("TEST 2: Vector Store")
    print("="*60)

    from app.ml.rag.vector_store import get_vector_store
    from app.ml.rag.embeddings import get_embedding_service

    try:
        store = get_vector_store(collection_name="test_collection")
        embedding_service = get_embedding_service()

        print(f"✓ Vector store initialized")
        print(f"  Collection: {store.collection_name}")

        # Add test documents
        docs = [
            "Deep breathing exercises can help manage anxiety and panic attacks.",
            "CBT techniques are evidence-based approaches for treating depression.",
            "Cultural sensitivity is important in mental health care."
        ]

        embeddings = embedding_service.embed_documents(docs)
        metadatas = [
            {"category": "anxiety", "source": "test"},
            {"category": "depression", "source": "test"},
            {"category": "cultural", "source": "test"}
        ]

        doc_ids = store.add_documents(
            documents=docs,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        print(f"\n✓ Added {len(doc_ids)} documents")
        print(f"  Count: {store.count()}")

        # Test search
        query = "How to deal with anxiety?"
        query_embedding = embedding_service.embed_query(query)
        results = store.search(query_embedding.tolist(), top_k=2)

        print(f"\n✓ Search completed")
        print(f"  Retrieved: {len(results['documents'])} documents")
        for i, (doc, dist) in enumerate(zip(results['documents'], results['distances'])):
            print(f"  {i+1}. [{dist:.3f}] {doc[:60]}...")

        # Cleanup
        store.delete_collection()
        print(f"\n✓ Test collection cleaned up")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_chunking():
    """Test document chunking"""
    print("\n" + "="*60)
    print("TEST 3: Document Chunking")
    print("="*60)

    from app.ml.rag.utils import DocumentChunker

    try:
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)

        text = """
        Cognitive Behavioral Therapy (CBT) is an evidence-based treatment for anxiety and depression.

        CBT helps you identify and challenge negative thought patterns. It teaches practical skills for managing emotions.

        Common CBT techniques include thought records, behavioral activation, and exposure therapy.
        These techniques have been proven effective in numerous clinical trials.
        """

        chunks = chunker.chunk_text(text, metadata={"source": "CBT Guide"})

        print(f"✓ Document chunked successfully")
        print(f"  Original length: {len(text)} characters")
        print(f"  Number of chunks: {len(chunks)}")

        for i, chunk in enumerate(chunks):
            print(f"\n  Chunk {i+1}:")
            print(f"    Length: {len(chunk.text)} chars")
            print(f"    Text: {chunk.text[:100]}...")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval():
    """Test retrieval service"""
    print("\n" + "="*60)
    print("TEST 4: Retrieval Service")
    print("="*60)

    from app.ml.rag.retrieval import create_retriever
    from app.ml.rag.vector_store import get_vector_store
    from app.ml.rag.embeddings import get_embedding_service

    try:
        # Setup
        store = get_vector_store(collection_name="test_retrieval")
        embedding_service = get_embedding_service()
        retriever = create_retriever(store, embedding_service)

        # Add test documents
        docs = [
            "Practice deep breathing: Inhale for 4 counts, hold for 4, exhale for 4.",
            "Progressive muscle relaxation helps reduce physical tension and anxiety.",
            "Mindfulness meditation involves focusing on the present moment without judgment.",
            "CBT teaches you to identify and challenge negative automatic thoughts.",
            "Exercise releases endorphins that improve mood and reduce stress."
        ]

        embeddings = embedding_service.embed_documents(docs)
        metadatas = [{"category": "anxiety", "technique": f"tech{i}"} for i in range(len(docs))]

        store.add_documents(
            documents=docs,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        print(f"✓ Test data added ({len(docs)} documents)")

        # Test retrieval
        query = "What can I do when I'm feeling anxious?"
        results = retriever.retrieve(query, top_k=3)

        print(f"\n✓ Retrieval completed")
        print(f"  Query: {query}")
        print(f"  Retrieved: {len(results)} documents\n")

        for result in results:
            print(f"  Rank {result.rank + 1}: [Score: {result.score:.3f}]")
            print(f"    {result.text[:80]}...")
            print(f"    Metadata: {result.metadata}\n")

        # Cleanup
        store.delete_collection()
        print(f"✓ Test collection cleaned up")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full RAG pipeline"""
    print("\n" + "="*60)
    print("TEST 5: Full RAG Pipeline")
    print("="*60)

    from app.ml.rag import get_rag_pipeline
    from app.ml.rag.knowledge_base import get_sample_knowledge_base

    try:
        # Initialize pipeline
        pipeline = get_rag_pipeline(collection_name="test_full_pipeline")
        print(f"✓ RAG pipeline initialized")

        # Add sample documents
        documents = get_sample_knowledge_base()[:5]  # Use first 5 for testing
        result = pipeline.add_documents(
            documents=documents,
            text_field="text",
            metadata_fields=["category", "source", "culture"]
        )

        print(f"\n✓ Documents added")
        print(f"  Total documents: {result['num_documents']}")
        print(f"  Total chunks: {result['num_chunks']}")

        # Test queries
        test_queries = [
            "How can I manage my anxiety?",
            "I'm feeling very sad and hopeless",
            "What are some cultural considerations in mental health?"
        ]

        for query in test_queries:
            print(f"\n{'─'*60}")
            print(f"Query: {query}")
            print(f"{'─'*60}")

            response = pipeline.query(
                query=query,
                top_k=3,
                max_context_length=500
            )

            print(f"\nRetrieved {response.metadata['num_retrieved']} documents")
            print(f"Average score: {response.metadata['avg_score']:.3f}")

            print(f"\nContext preview:")
            print(f"{response.context[:300]}...\n")

            for i, doc in enumerate(response.retrieved_docs, 1):
                cat = doc.metadata.get('category', 'N/A')
                print(f"  {i}. [{doc.score:.3f}] Category: {cat}")

        # Get stats
        stats = pipeline.get_stats()
        print(f"\n✓ Pipeline statistics:")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Total chunks: {stats['num_documents']}")
        print(f"  Model: {stats['embedding_model']['model_name']}")

        # Cleanup
        pipeline.delete_all()
        print(f"\n✓ Test data cleaned up")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG PIPELINE COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        ("Embedding Service", test_embedding_service),
        ("Vector Store", test_vector_store),
        ("Document Chunking", test_document_chunking),
        ("Retrieval Service", test_retrieval),
        ("Full Pipeline", test_full_pipeline)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    return passed == total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test RAG pipeline")
    parser.add_argument(
        "--test",
        choices=["all", "embedding", "vector", "chunking", "retrieval", "pipeline"],
        default="all",
        help="Which test to run"
    )

    args = parser.parse_args()

    if args.test == "all":
        success = run_all_tests()
    elif args.test == "embedding":
        success = test_embedding_service()
    elif args.test == "vector":
        success = test_vector_store()
    elif args.test == "chunking":
        success = test_document_chunking()
    elif args.test == "retrieval":
        success = test_retrieval()
    elif args.test == "pipeline":
        success = test_full_pipeline()

    sys.exit(0 if success else 1)
