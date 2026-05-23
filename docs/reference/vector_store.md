---
title: "Vector Store Module"
description: "Unified interface for FAISS, Pinecone, Weaviate, Qdrant, Milvus, and PgVector with hybrid search."
icon: "database"
---

`semantica.vector_store` provides a unified API for storing and searching vector embeddings across all major backends. Swap backends with a one-line change — no application code changes needed.

## What You Get

<CardGroup cols={2}>
  <Card title="VectorStore" icon="database">
    Unified interface across FAISS, Pinecone, Weaviate, Qdrant, Milvus, and PgVector.
  </Card>
  <Card title="HybridSearch" icon="magnifying-glass">
    Combine dense vector similarity with sparse keyword/BM25 filtering and configurable fusion strategies.
  </Card>
  <Card title="MetadataStore" icon="table">
    Rich metadata indexing and schema management — query by field values without a vector.
  </Card>
  <Card title="NamespaceManager" icon="folder-tree">
    Multi-tenant namespace isolation — structural separation, not just metadata filters.
  </Card>
  <Card title="Batch Operations" icon="layer-group">
    Bulk add, delete, and metadata updates — automatically chunked for memory efficiency.
  </Card>
  <Card title="FAISS Index Types" icon="chart-scatter">
    Flat, IVF, HNSW, and PQ index types with full configuration control.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Create a vector store">
    ```python
    from semantica.vector_store import VectorStore

    # In-memory (development)
    store = VectorStore(backend="inmemory", dimension=768)

    # FAISS (local production — persists to disk)
    store = VectorStore(backend="faiss", dimension=768, index_path="store.faiss")
    ```
  </Step>
  <Step title="Add vectors">
    ```python
    store.add_vectors(
        embeddings=embeddings,
        ids=["doc1", "doc2"],
        metadata=[{"title": "Document 1"}, {"title": "Document 2"}]
    )
    ```
  </Step>
  <Step title="Search by semantic similarity">
    ```python
    results = store.search(query_vector, top_k=10)
    for r in results:
        print(f"{r['id']} — score: {r['score']:.3f}")
        print(f"  metadata: {r['metadata']}")
    ```
  </Step>
  <Step title="Filter results by metadata">
    ```python
    # Equality, range, and set filters
    results = store.search(query_vector, filters={
        "$and": [
            {"category": "research"},
            {"year": {"$gte": 2022}}
        ]
    })
    ```
  </Step>
</Steps>

## Backends

<Tabs>
  <Tab title="FAISS">

```python
store = VectorStore(
    backend="faiss",
    dimension=768,
    index_type="IVF",       # "Flat" | "IVF" | "HNSW" | "PQ"
    index_path="store.faiss"
)
```

Best for: local development, on-premise production with no external services. No API key required.

  </Tab>
  <Tab title="Pinecone">

```bash
pip install "semantica[pinecone]"
```

```python
store = VectorStore(
    backend="pinecone",
    dimension=768,
    api_key=os.getenv("PINECONE_API_KEY"),
    index_name="semantica-index",
    environment="us-east-1-aws"
)
```

  </Tab>
  <Tab title="Weaviate">

```bash
pip install "semantica[weaviate]"
```

```python
store = VectorStore(
    backend="weaviate",
    dimension=768,
    url="http://localhost:8080",
    class_name="Document"
)
```

  </Tab>
  <Tab title="Qdrant">

```bash
pip install "semantica[qdrant]"
```

```python
store = VectorStore(
    backend="qdrant",
    dimension=768,
    url="http://localhost:6333",
    collection_name="semantica"
)
```

  </Tab>
  <Tab title="PgVector">

```bash
pip install "semantica[pgvector]"
```

```python
store = VectorStore(
    backend="pgvector",
    dimension=768,
    connection_string="postgresql://user:pass@localhost/db",
    table_name="embeddings"
)
```

See the [PgVector Guide](../vector_stores/pgvector) for full setup.

  </Tab>
</Tabs>

## Hybrid Search

Combine vector similarity with keyword/metadata filters for higher precision:

```python
results = store.hybrid_search(
    query_vector=query_embedding,
    query_text="machine learning",  # keyword component
    top_k=10,
    alpha=0.7,                      # 0.0 = keyword only, 1.0 = vector only
    filters={"category": "research", "year": {"$gte": 2022}}
)
```

## Metadata Filtering

```python
# Equality
results = store.search(query_vector, filters={"author": "John Smith"})

# Range
results = store.search(query_vector, filters={"date": {"$gte": "2023-01-01"}})

# Set membership
results = store.search(query_vector, filters={"tag": {"$in": ["ai", "ml"]}})

# Compound AND
results = store.search(query_vector, filters={
    "$and": [
        {"category": "research"},
        {"year": {"$gte": 2022}}
    ]
})
```

## Namespace Isolation

Isolate vectors per tenant, project, or use case:

```python
store = VectorStore(backend="faiss", dimension=768)

# Write to separate namespaces
store.add_vectors(embeddings_a, ids_a, namespace="tenant_a")
store.add_vectors(embeddings_b, ids_b, namespace="tenant_b")

# Search is scoped to the specified namespace
results = store.search(query_vector, namespace="tenant_a")
```

## Batch Operations

```python
# Batch add — automatically chunked for memory efficiency
store.add_vectors_batch(embeddings_list, ids_list, batch_size=1000)

# Batch delete
store.delete_vectors(ids=["doc1", "doc2", "doc3"])

# Update metadata without re-embedding
store.update_metadata("doc1", {"status": "archived", "reviewed": True})
```

## Backend Comparison

| Backend | Deployment | API Key | Hybrid Search | Best For |
| ------- | ---------- | ------- | ------------- | -------- |
| FAISS | Local | No | No | On-premise, offline |
| Pinecone | Cloud | Yes | Yes | Managed cloud, serverless |
| Weaviate | Self-hosted / Cloud | Optional | Yes | Rich metadata filtering |
| Qdrant | Self-hosted / Cloud | Optional | Yes | High-performance filtering |
| Milvus | Self-hosted | No | Yes | Large-scale production |
| PgVector | PostgreSQL | No | Limited | Postgres-native integration |
| In-memory | Process | No | No | Development, testing |

## HybridSearch

`HybridSearch` is the low-level class behind `store.hybrid_search()` — use it directly when you need custom result fusion logic:

```python
from semantica.vector_store import HybridSearch, VectorStore

store  = VectorStore(backend="faiss", dimension=768)
hybrid = HybridSearch(vector_store=store)

results = hybrid.search(
    query_vector=query_embedding,
    query_text="machine learning frameworks",
    top_k=20,
    vector_weight=0.7,       # weight for vector similarity leg
    keyword_weight=0.3,      # weight for BM25/keyword leg
    fusion="rrf",            # "rrf" (Reciprocal Rank Fusion) | "weighted_avg"
    filters={"category": "research", "year": {"$gte": 2022}},
    deduplicate=True,
)

for r in results:
    print(f"{r['id']}  vector_score={r['vector_score']:.3f}  final_score={r['score']:.3f}")
```

| Fusion strategy | Description |
| --------------- | ----------- |
| `rrf` | Reciprocal Rank Fusion — rank-based combination, robust to score scale differences |
| `weighted_avg` | Weighted average of normalised scores — requires `vector_weight` + `keyword_weight` = 1.0 |

## MetadataStore

`MetadataStore` manages structured metadata attached to vectors — query by field values without a vector:

```python
from semantica.vector_store import MetadataStore

meta_store = MetadataStore()

meta_store.register_schema({
    "author":   "str",
    "year":     "int",
    "category": "str",
    "score":    "float",
})

meta_store.add("doc1", {"author": "Alice", "year": 2024, "category": "research"})
meta_store.add("doc2", {"author": "Bob",   "year": 2023, "category": "review"})

results = meta_store.filter({"category": "research", "year": {"$gte": 2023}})
meta    = meta_store.get("doc1")
meta_store.update("doc1", {"score": 0.92})
```

## NamespaceManager

Isolates vector collections per tenant, project, or model version:

```python
from semantica.vector_store import NamespaceManager, VectorStore

base_store = VectorStore(backend="faiss", dimension=768)
ns_manager  = NamespaceManager(vector_store=base_store)

ns_manager.create_namespace("tenant_a", description="Customer A data")
ns_manager.create_namespace("tenant_b", description="Customer B data")

ns_manager.add_vectors("tenant_a", embeddings_a, ids_a, metadata_a)
ns_manager.add_vectors("tenant_b", embeddings_b, ids_b, metadata_b)

# Search is scoped — tenant_a never sees tenant_b's data
results = ns_manager.search("tenant_a", query_vector, top_k=10)

for ns in ns_manager.list_namespaces():
    print(f"{ns['name']}: {ns['vector_count']} vectors")

ns_manager.delete_namespace("tenant_a")
```

## FAISS Index Type Reference

| Index | Memory | Speed | Accuracy | When to Use |
| ----- | ------ | ----- | -------- | ----------- |
| `Flat` | High | Slow | Exact (100%) | < 100K vectors, correctness critical |
| `IVF` | Medium | Fast | ~95–98% | 100K–10M vectors, good balance |
| `HNSW` | Medium-High | Very fast | ~97–99% | Low latency, production retrieval |
| `PQ` | Low | Fast | ~90–95% | Millions of vectors, memory-constrained |

```python
# Flat — brute-force exact search
store = VectorStore(backend="faiss", dimension=768, index_type="Flat")

# IVF — inverted file index with nlist clusters
store = VectorStore(backend="faiss", dimension=768, index_type="IVF", nlist=100)

# HNSW — hierarchical navigable small world graph
store = VectorStore(backend="faiss", dimension=768, index_type="HNSW", M=16, ef_construction=200)

# PQ — product quantization for memory efficiency
store = VectorStore(backend="faiss", dimension=768, index_type="PQ", m=8)
```

## Similarity Metrics

| Metric | Constructor arg | Distance → Similarity | Best For |
| ------ | --------------- | --------------------- | -------- |
| Cosine | `metric="cosine"` | `1 - cosine_distance` | Text, embeddings |
| L2 (Euclidean) | `metric="l2"` | `1 / (1 + distance)` | Image features |
| Inner Product | `metric="ip"` | raw dot product | Recommendation systems |

```python
store = VectorStore(backend="faiss", dimension=768, metric="cosine")
```

## Tips and Common Pitfalls

<Warning>
  **Match vector dimension to your embedding model.** The `dimension` parameter must exactly match your embedding model's output size — `all-MiniLM-L6-v2` = 384, `all-mpnet-base-v2` = 768, `bge-large-en-v1.5` = 1024. A mismatch raises an error at insert time, not at store creation.
</Warning>

<Tip>
  **Use `Flat` index only for small datasets.** Flat (brute-force) search has perfect recall but O(n) query time. At 500K+ vectors, switch to `IVF` or `HNSW` — they sacrifice less than 5% recall for 100–1000x speedup.
</Tip>

<Warning>
  **Don't search without normalizing first.** If you disabled `normalize=True` in `EmbeddingGenerator`, compute cosine similarity with `metric="cosine"` (which normalizes internally). Raw dot product on un-normalized vectors produces incorrect similarity rankings.
</Warning>

<Tip>
  **Use `hybrid_search` for precision-sensitive workloads.** Pure vector search finds semantically similar results but may miss keyword matches important to the user. Hybrid search (vector + BM25) combines both signals — especially valuable for domain-specific terminology.
</Tip>

<Tip>
  **Use `NamespaceManager` for multi-tenant applications.** Storing all tenants' vectors in the same collection and filtering by metadata at query time is slow and leaks data if a filter is accidentally omitted. Namespace isolation is both faster (smaller search space) and safer (structural isolation).
</Tip>

<Warning>
  **Persist FAISS indexes to disk.** `VectorStore(backend="faiss", index_path="store.faiss")` saves the index to disk on each write. Without a path, the index is in-memory only and is lost on process exit.
</Warning>

<Tip>
  **Update metadata without re-embedding.** `store.update_metadata(id, {...})` changes attached fields (status, tags, review date) without re-running the embedding model. Use this for state changes that don't affect semantic content.
</Tip>

<CardGroup cols={2}>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Generate the vectors stored here.
  </Card>
  <Card title="Context" icon="brain" href="context">
    AgentContext uses VectorStore for memory retrieval.
  </Card>
  <Card title="PgVector Guide" icon="database" href="../vector_stores/pgvector">
    PostgreSQL vector storage with pgvector extension.
  </Card>
  <Card title="Ingest" icon="download" href="ingest">
    Ingest documents before embedding and storing.
  </Card>
</CardGroup>
