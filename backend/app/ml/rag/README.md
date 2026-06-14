# RAG (Retrieval-Augmented Generation) Pipeline

## Overview

The RAG pipeline enhances the mental health chatbot with evidence-based, culturally-sensitive responses by retrieving relevant information from a curated knowledge base.

## Architecture

```
User Query
    ↓
Query Embedding (Sentence Transformers)
    ↓
Vector Search (ChromaDB)
    ↓
Retrieval & Ranking
    ↓
Context Building
    ↓
Response Generation (with retrieved context)
    ↓
User Response
```

## Components

### 1. Embeddings (`embeddings/`)
- **EmbeddingService**: Converts text to vector embeddings
- Model: `all-MiniLM-L6-v2` (384 dimensions, fast, good quality)
- Singleton pattern for efficiency

### 2. Vector Store (`vector_store/`)
- **ChromaVectorStore**: Persistent vector database
- Stores document chunks with embeddings and metadata
- Supports similarity search and filtering

### 3. Document Processing (`utils/`)
- **TextProcessor**: Cleans and normalizes text
- **DocumentChunker**: Splits documents into manageable chunks
- **ContextBuilder**: Builds context for prompts

### 4. Retrieval (`retrieval/`)
- **SemanticRetriever**: Semantic similarity search
- **HybridRetriever**: Combines semantic + keyword search
- Supports diversity-based retrieval (MMR)

### 5. Pipeline Orchestrator (`rag_pipeline.py`)
- **RAGPipeline**: Main interface for RAG operations
- Coordinates all components
- Handles document ingestion and querying

### 6. Knowledge Base (`knowledge_base/`)
- Curated mental health content
- Categories: CBT, mindfulness, cultural, crisis, trauma, etc.
- Diverse, evidence-based information

### 7. Configuration (`config.py`)
- Centralized settings
- Presets: fast, balanced, quality, multilingual

### 8. Prompts (`prompts/`)
- Templates for different scenarios
- Crisis, cultural, anxiety, depression, etc.

## Setup & Usage

### 1. Initialize Knowledge Base

```bash
cd backend
python -m app.ml.rag.knowledge_base.initialize_kb --reset --test
```

This will:
- Create the vector database
- Load sample mental health documents
- Generate embeddings
- Test retrieval with sample queries

### 2. Test RAG Pipeline

```bash
# Run all tests
python -m app.ml.rag.test_rag --test all

# Run specific test
python -m app.ml.rag.test_rag --test pipeline
```

### 3. Use in Chat Service

The RAG pipeline is automatically integrated into the chat service:

```python
from app.ml.rag import get_rag_pipeline

# Get pipeline instance
pipeline = get_rag_pipeline()

# Query for relevant context
response = pipeline.query(
    query="How can I manage my anxiety?",
    top_k=5,
    metadata_filter={"category": "anxiety"}
)

# Access retrieved documents
for doc in response.retrieved_docs:
    print(f"Score: {doc.score}, Text: {doc.text}")

# Access built context
print(response.context)
```

## Features

### Semantic Search
- Finds conceptually similar content, not just keyword matches
- Example: "I'm worried" retrieves anxiety management techniques

### Metadata Filtering
- Filter by category, culture, topic
- Example: Only retrieve crisis protocols when risk is high

### Diversity Retrieval
- MMR (Maximal Marginal Relevance)
- Balances relevance and diversity
- Avoids redundant information

### Cultural Sensitivity
- Culturally-adapted content for different populations
- Asian collectivist approaches
- Latinx familismo considerations
- African Ubuntu philosophy

### Crisis Prioritization
- Automatically retrieves crisis protocols for high-risk situations
- Evidence-based suicide prevention resources

## Knowledge Base Categories

1. **CBT** - Cognitive Behavioral Therapy techniques
2. **Mindfulness** - Meditation and mindfulness practices
3. **Cultural** - Culturally-adapted interventions
4. **Crisis** - Crisis intervention and suicide prevention
5. **Trauma** - Trauma-informed care principles
6. **Selfcare** - Holistic wellness strategies
7. **Anxiety** - Anxiety management techniques
8. **Depression** - Depression support strategies

## Configuration

### Environment Variables
```bash
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_COLLECTION_NAME=mental_health_docs
RAG_TOP_K=5
RAG_USE_DIVERSITY=true
```

### Load Preset
```python
from app.ml.rag.config import load_preset

# Fast retrieval
load_preset("fast")

# Best quality (slower)
load_preset("quality")

# Multilingual support
load_preset("multilingual")
```

## Adding New Documents

### From Code
```python
from app.ml.rag import get_rag_pipeline

pipeline = get_rag_pipeline()

documents = [
    {
        "text": "Your mental health content here...",
        "category": "anxiety",
        "source": "Clinical Guidelines 2024",
        "culture": "universal"
    }
]

result = pipeline.add_documents(
    documents=documents,
    text_field="text",
    metadata_fields=["category", "source", "culture"]
)
```

### From Files
```python
# Load from JSON, CSV, or text files
# TODO: Implement document loaders
```

## Performance

### Benchmarks (on sample queries)
- Query embedding: ~10ms
- Vector search (1000 docs): ~20ms
- Total retrieval time: ~30-50ms
- Memory: ~200MB (for all-MiniLM-L6-v2 model)

### Optimization Tips
1. Use `fast` preset for real-time applications
2. Enable caching for repeated queries
3. Adjust `top_k` based on context window limits
4. Use metadata filters to narrow search space

## Integration with Chat Service

The chat service automatically uses RAG when enabled:

```python
# In chat_service.py
def __init__(self, db: Session, use_rag: bool = True):
    if use_rag:
        self.rag_pipeline = get_rag_pipeline()
```

Retrieved context is used to:
1. Provide evidence-based responses
2. Ground responses in knowledge base
3. Reduce hallucinations
4. Improve cultural sensitivity
5. Enhance crisis support

## Monitoring & Analytics

Track RAG performance:
- Retrieval quality (relevance scores)
- Knowledge base coverage
- Response grounding percentage
- Source attribution
- Cultural diversity in retrievals

## Future Enhancements

- [ ] Cross-encoder reranking for better precision
- [ ] Hybrid search (BM25 + semantic)
- [ ] User feedback loop for retrieval quality
- [ ] Automatic knowledge base expansion
- [ ] Multilingual embeddings
- [ ] Fine-tuned embeddings for mental health domain
- [ ] Real-time knowledge base updates
- [ ] A/B testing different retrieval strategies

## Troubleshooting

### Issue: Slow retrieval
- Use `fast` preset
- Reduce `top_k`
- Enable caching

### Issue: Poor relevance
- Use `quality` preset (better embeddings)
- Adjust chunk size
- Add more diverse documents

### Issue: Out of memory
- Use smaller embedding model
- Reduce batch size
- Clear vector store cache

## References

- Sentence Transformers: https://www.sbert.net/
- ChromaDB: https://www.trychroma.com/
- RAG Paper: https://arxiv.org/abs/2005.11401
