---
title: "Embeddings Module"
description: "Text and graph embedding generation — Sentence-Transformers, FastEmbed, OpenAI, BGE, LlamaStore, with pooling strategies and graph embedding managers."
icon: "vector-square"
---

> Unified interface for generating vector representations of text, nodes, and graphs.

---

## Overview

The **Embeddings Module** converts text and graph structures into dense vectors for semantic search, entity resolution, and GraphRAG retrieval. It abstracts multiple providers behind a single API and supports five pooling strategies.

<CardGroup cols={2}>
  <Card title="EmbeddingGenerator" icon="bolt">
    Main entry point — provider-agnostic text embedding generation.
  </Card>
  <Card title="TextEmbedder" icon="text-size">
    Text-specific embedding with batching and caching.
  </Card>
  <Card title="GraphEmbeddingManager" icon="diagram-project">
    Node and subgraph embedding for structural similarity.
  </Card>
  <Card title="VectorEmbeddingManager" icon="database">
    Embedding lifecycle for vector store integration.
  </Card>
  <Card title="ProviderStore" icon="server">
    Pluggable backends: OpenAI, BGE, FastEmbed, LlamaStore.
  </Card>
  <Card title="Pooling Strategies" icon="layer-group">
    Mean, Max, CLS, Attention, Hierarchical pooling.
  </Card>
</CardGroup>

---

## EmbeddingGenerator

Main entry point — handles provider selection and batching:

```python
from semantica.embeddings import EmbeddingGenerator

# Sentence-Transformers (default, free, local)
generator = EmbeddingGenerator(model="sentence-transformers")
embeddings = generator.generate(["Text 1", "Text 2"])

# Specific model
generator = EmbeddingGenerator(model="BAAI/bge-large-en-v1.5")
embeddings = generator.generate(texts)

# OpenAI
import os
generator = EmbeddingGenerator(
    model="openai",
    model_name="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)

# FastEmbed (fast CPU-optimized)
generator = EmbeddingGenerator(model="fastembed")
```

---

## Supported Models

| Provider | Model | Dimension | Notes |
|----------|-------|-----------|-------|
| `sentence-transformers` | `all-MiniLM-L6-v2` | 384 | Default, fast, free |
| `sentence-transformers` | `all-mpnet-base-v2` | 768 | Higher quality |
| `bge` | `BAAI/bge-large-en-v1.5` | 1024 | State-of-the-art retrieval |
| `fastembed` | `BAAI/bge-small-en-v1.5` | 384 | Fast, CPU-optimized |
| `openai` | `text-embedding-3-small` | 1536 | OpenAI API |
| `openai` | `text-embedding-3-large` | 3072 | OpenAI API, highest quality |
| `llama` | any Ollama model | varies | Local inference |

---

## TextEmbedder

Specialized for text with automatic batching:

```python
from semantica.embeddings import TextEmbedder

embedder = TextEmbedder(model="sentence-transformers", cache_dir=".emb_cache")

# Single text
embedding = embedder.embed("Hello world")

# Batch
embeddings = embedder.embed_batch(
    ["Text 1", "Text 2", ..., "Text 10000"],
    batch_size=128,
    show_progress=True
)
```

---

## Provider Stores

Each provider implements the `ProviderStore` interface and can be used independently:

```python
from semantica.embeddings import (
    OpenAIStore, BGEStore, FastEmbedStore, LlamaStore,
    ProviderStoreFactory
)

# OpenAI
store = OpenAIStore(api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-small")
embedding = store.embed("Hello world")

# BGE (Sentence-Transformers wrapper)
store = BGEStore(model="BAAI/bge-large-en-v1.5")
embedding = store.embed("Hello world")

# FastEmbed
store = FastEmbedStore(model="BAAI/bge-small-en-v1.5")
embedding = store.embed("Hello world")

# LlamaStore (Ollama local)
store = LlamaStore(model="llama3.2", base_url="http://localhost:11434")
embedding = store.embed("Hello world")

# Auto-select from config
store = ProviderStoreFactory.create(provider="openai", model="text-embedding-3-small")
```

---

## Pooling Strategies

Control how token-level embeddings are aggregated into a single vector:

```python
from semantica.embeddings import (
    MeanPooling, MaxPooling, CLSPooling,
    AttentionPooling, HierarchicalPooling, PoolingStrategyFactory
)

# Mean pooling (default — best for most tasks)
pooler = MeanPooling()
pooled = pooler.pool(token_embeddings)

# Max pooling (captures strongest features)
pooler = MaxPooling()

# CLS token pooling (first token — good for classification)
pooler = CLSPooling()

# Attention-weighted pooling
pooler = AttentionPooling()

# Hierarchical: chunk-level → global mean (best for long documents)
pooler = HierarchicalPooling(chunk_size=512)

# Create from config
pooler = PoolingStrategyFactory.create(strategy="mean")
```

---

## GraphEmbeddingManager

Embed graph nodes and subgraphs for structural similarity and GraphRAG:

```python
from semantica.embeddings import GraphEmbeddingManager

manager = GraphEmbeddingManager(
    text_embedder=TextEmbedder(model="sentence-transformers"),
    graph_store=graph_store
)

# Embed all nodes
node_embeddings = manager.embed_nodes(kg)

# Embed a specific subgraph (for GraphRAG context)
subgraph_embedding = manager.embed_subgraph(
    kg, center_node="Apple Inc.", hops=2
)

# Find similar nodes
similar = manager.find_similar_nodes("apple_inc", top_k=5)
```

---

## VectorEmbeddingManager

Manages the full embedding lifecycle for vector store integration:

```python
from semantica.embeddings import VectorEmbeddingManager
from semantica.vector_store import VectorStore

vector_store = VectorStore(backend="faiss", dimension=768)

manager = VectorEmbeddingManager(
    embedder=TextEmbedder(model="sentence-transformers"),
    vector_store=vector_store
)

# Embed and store documents
ids = manager.embed_and_store(documents, metadata=metadata_list)

# Search
results = manager.search("machine learning algorithms", top_k=10)
```

---

## Similarity Computation

```python
from semantica.embeddings import calculate_similarity

score = calculate_similarity(embedding_a, embedding_b, method="cosine")
# → 0.0 to 1.0

# Euclidean distance converted to similarity
score = calculate_similarity(embedding_a, embedding_b, method="euclidean")
```

---

## Convenience Functions

```python
from semantica.embeddings import (
    embed_text, generate_embeddings, calculate_similarity,
    pool_embeddings, check_available_providers
)

# Single text
emb = embed_text("Hello world", method="sentence_transformers")

# Batch
embs = generate_embeddings(texts, method="openai")

# Check what's installed
providers = check_available_providers()
# → {"sentence_transformers": True, "fastembed": True, "openai": False}
```

---

## GPU Acceleration

```python
generator = EmbeddingGenerator(model="sentence-transformers", device="cuda")
# device: "cpu" | "cuda" | "mps"
```

---

## Caching

Embedding cache reuse is used by Distance Intelligence (v0.5.0) to avoid recomputing embeddings for large distance matrix calculations:

```python
embedder = TextEmbedder(
    model="sentence-transformers",
    cache_dir=".embeddings_cache",
    cache_ttl=3600          # TTL in seconds
)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Vector Store" icon="database" href="vector_store">
    Store and search the generated embeddings.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk text before embedding.
  </Card>
  <Card title="KG Module" icon="diagram-project" href="kg">
    Distance Intelligence uses graph embeddings.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Semantic deduplication uses embeddings for entity resolution.
  </Card>
</CardGroup>
