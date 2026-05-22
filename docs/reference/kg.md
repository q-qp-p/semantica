---
title: "Knowledge Graph Module"
description: "Graph construction, temporal models, analytics, and distance intelligence."
icon: "diagram-project"
---

> High-level KG construction, management, and analysis system.

---

## Overview

The **Knowledge Graph (KG) Module** transforms extracted entities and relationships into structured, queryable knowledge graphs. It includes temporal support, graph analytics, node embeddings, and distance intelligence (v0.5.0).

<CardGroup cols={2}>
  <Card title="KG Construction" icon="hammer">
    Build graphs from entities and relationships with automatic entity merging.
  </Card>
  <Card title="Temporal Graphs" icon="clock">
    Time-aware edges (`valid_from`, `valid_until`) and point-in-time queries (v0.4.0).
  </Card>
  <Card title="Graph Analytics" icon="chart-bar">
    Centrality, community detection, and connectivity analysis.
  </Card>
  <Card title="Distance Intelligence" icon="compass">
    Semantic neighborhoods, distance matrices, and ego-mode exploration (v0.5.0).
  </Card>
  <Card title="Provenance" icon="link">
    Track the source and lineage of every node and edge.
  </Card>
  <Card title="Entity Resolution" icon="user-check">
    Resolve and merge similar entities using fuzzy matching and semantic similarity.
  </Card>
</CardGroup>

<Tip>
  **Related modules:** Use `semantica.conflicts` for conflict detection and `semantica.deduplication` for advanced entity resolution.
</Tip>

---

## GraphBuilder

Constructs knowledge graphs from raw entities and relationships.

```python
from semantica.kg import GraphBuilder

builder = GraphBuilder(merge_entities=True)
kg = builder.build(entities=entities, relationships=relationships)
```

| Method | Description |
|--------|-------------|
| `build(sources)` | Build graph from multiple data sources |
| `build_single_source(data)` | Build graph from single data source |
| `merge_entities()` | Merge duplicate entities during building |

---

## Temporal Knowledge Graphs (v0.4.0)

```python
from semantica.kg import TemporalKnowledgeGraph, TemporalGraphQuery
from datetime import datetime

# Build temporal graph
tkg = TemporalKnowledgeGraph()
tkg.add_node("ceo_role", valid_from=datetime(2020, 1, 1), valid_until=datetime(2023, 6, 1))
tkg.add_edge("alice", "acme_corp", "ceo_of",
             valid_from=datetime(2020, 1, 1), valid_until=datetime(2023, 6, 1))

# Point-in-time query
snapshot = tkg.at(datetime(2021, 6, 15))

# Query evolution
query = TemporalGraphQuery(tkg)
snapshot_2020 = query.at_time("2020-01-01")
snapshot_2023 = query.at_time("2023-01-01")
diff = snapshot_2023.minus(snapshot_2020)
print(f"New nodes since 2020: {len(diff.nodes)}")
```

Supports all 13 Allen interval algebra relations (before, after, meets, overlaps, during, starts, finishes, equals, and their inverses). OWL-Time export available.

---

## Distance Intelligence (v0.5.0)

```python
from semantica.kg import DistanceCalculator

calc = DistanceCalculator(kg)

# Semantic neighborhood of a node
neighborhood = calc.semantic_neighborhood("Apple Inc.", radius=0.4)

# N×N distance matrix
matrix = calc.distance_matrix(["Apple Inc.", "Google", "Microsoft"])

# Distance band classification: "near" | "mid" | "far"
bands = calc.classify_bands(neighborhood)
```

---

## Graph Analytics

### Centrality Analysis

```python
from semantica.kg import CentralityCalculator

calculator = CentralityCalculator()
centrality = calculator.calculate_degree_centrality(graph)
pagerank_scores = calculator.calculate_pagerank(graph, damping_factor=0.85)
top_nodes = calculator.get_top_nodes(centrality, top_k=10)
```

| Method | Algorithm |
|--------|-----------|
| `calculate_degree_centrality()` | Degree-based importance |
| `calculate_betweenness_centrality()` | Bridge-based importance |
| `calculate_closeness_centrality()` | Distance-based importance |
| `calculate_eigenvector_centrality()` | Influence-based importance |
| `calculate_pagerank()` | PageRank scores |
| `calculate_all_centrality()` | All measures at once |

### Community Detection

```python
from semantica.kg import CommunityDetector

detector = CommunityDetector()
communities = detector.detect_communities(graph, algorithm="louvain")
metrics = detector.calculate_community_metrics(graph, communities)
leiden_communities = detector.detect_communities_leiden(graph, resolution=1.2)
```

Algorithms: Louvain, Leiden, Label Propagation, K-Clique Communities.

### Path Finding

```python
from semantica.kg import PathFinder

finder = PathFinder()
path = finder.dijkstra_shortest_path(graph, "node_a", "node_b")
paths = finder.all_shortest_paths(graph, "source", "target")
k_paths = finder.find_k_shortest_paths(graph, "source", "target", k=3)
```

Algorithms: Dijkstra, A\*, BFS, All Shortest Paths, K-Shortest Paths.

### Link Prediction

```python
from semantica.kg import LinkPredictor

predictor = LinkPredictor(method="preferential_attachment")
links = predictor.predict_links(graph, top_k=20)
score = predictor.score_link(graph, "node_a", "node_b")
```

Algorithms: Preferential Attachment, Common Neighbors, Jaccard, Adamic-Adar, Resource Allocation.

### Node Embeddings

```python
from semantica.kg import NodeEmbedder

embedder = NodeEmbedder(method="node2vec", embedding_dimension=128)
embeddings = embedder.compute_embeddings(graph_store, ["Entity"], ["RELATED_TO"])
similar_nodes = embedder.find_similar_nodes(graph_store, "entity_123", top_k=10)
```

Algorithms: Node2Vec, DeepWalk, Word2Vec.

---

## Algorithm Summary

| Category | Algorithms | Use Cases |
|----------|------------|-----------|
| Node Embeddings | Node2Vec, DeepWalk, Word2Vec | Structural similarity, node representation |
| Similarity Analysis | Cosine, Euclidean, Manhattan, Correlation | Node similarity, recommendation |
| Path Finding | Dijkstra, A\*, BFS, K-Shortest | Route planning, network analysis |
| Link Prediction | Preferential Attachment, Jaccard, Adamic-Adar | Network completion |
| Centrality | Degree, Betweenness, Closeness, PageRank | Influence analysis |
| Community Detection | Louvain, Leiden, Label Propagation | Social analysis, clustering |
| Connectivity | Components, Bridges, Density | Network robustness |

---

## Configuration

```yaml
kg:
  resolution:
    threshold: 0.9
    strategy: semantic

  temporal:
    enabled: true
    default_validity: infinite
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Graph Store" icon="server" href="graph_store">
    Persistence layer (Neo4j, FalkorDB, Apache AGE).
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Data source for entities and relationships.
  </Card>
  <Card title="Visualization" icon="chart-bar" href="visualization">
    Visualize knowledge graphs interactively.
  </Card>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Conflict detection and resolution.
  </Card>
</CardGroup>

### Cookbook

- [Building Knowledge Graphs](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/07_Building_Knowledge_Graphs.ipynb) — fundamentals of KG construction · Beginner
- [Your First Knowledge Graph](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/08_Your_First_Knowledge_Graph.ipynb) — entity extraction to visualization · Beginner
- [Graph Analytics](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/10_Graph_Analytics.ipynb) — centrality and community detection · Intermediate
- [Advanced Graph Analytics](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/02_Advanced_Graph_Analytics.ipynb) — PageRank, Louvain, shortest path · Advanced
- [Temporal Knowledge Graphs](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/10_Temporal_Knowledge_Graphs.ipynb) — temporal logic and graph evolution · Advanced
