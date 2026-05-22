---
title: "Visualization Module"
description: "Interactive and static knowledge graph, ontology, embedding, and temporal visualization."
icon: "chart-bar"
---

> Comprehensive visualization suite for knowledge graphs, ontologies, embeddings, and temporal data.

---

## GraphVisualizer

```python
from semantica.visualization import GraphVisualizer

viz = GraphVisualizer()

# Interactive HTML (PyVis)
viz.visualize(graph, output="graph.html")

# Static image (Matplotlib)
viz.visualize(graph, output="graph.png", backend="matplotlib")

# Open directly in browser
viz.show(graph)
```

---

## Layout Options

```python
viz.visualize(
    graph,
    output="graph.html",
    layout="force_directed",   # force_directed | hierarchical | circular | spring
    node_color_by="type",      # color nodes by attribute
    edge_label="relation",     # show edge labels
    max_nodes=500              # limit for large graphs
)
```

---

## Ontology Visualization

```python
from semantica.visualization import OntologyVisualizer

viz = OntologyVisualizer()
viz.visualize(ontology, output="ontology.html")

# Hierarchy view
viz.visualize_hierarchy(ontology, output="hierarchy.html")
```

---

## Embedding Visualization

```python
from semantica.visualization import EmbeddingVisualizer

viz = EmbeddingVisualizer()

# UMAP projection
viz.visualize(
    embeddings=embeddings,
    labels=labels,
    output="embeddings.html",
    method="umap"       # umap | tsne | pca
)
```

---

## Temporal Visualization

```python
from semantica.visualization import TemporalVisualizer

viz = TemporalVisualizer()

# Timeline of graph changes
viz.visualize_timeline(temporal_kg, output="timeline.html")

# Animated graph evolution
viz.animate(temporal_kg, output="evolution.html", fps=2)
```

---

## Distance / Ego-Mode Visualization (v0.5.0)

```python
from semantica.visualization import DistanceVisualizer

viz = DistanceVisualizer()

# Ego-mode: neighborhood of a node colored by distance band
viz.visualize_ego(
    graph,
    center_node="Apple Inc.",
    output="ego.html",
    radius=0.5
)

# Distance matrix heatmap
viz.visualize_distance_matrix(
    matrix=distance_matrix,
    labels=node_labels,
    output="distance_heatmap.html"
)
```

---

## Graph Explorer (v0.4.0/v0.5.0)

The full-featured browser UI — bidirectional path finding, indexed search (0.004ms on 118k nodes), workspace management.

```python
from semantica.explorer import start_explorer

start_explorer(graph=kg, port=8080)
# Opens at http://localhost:8080
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being visualized.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Visualize ontology structure.
  </Card>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Visualize embedding space.
  </Card>
  <Card title="Explorer" icon="globe" href="explorer">
    Full Knowledge Explorer UI.
  </Card>
</CardGroup>
