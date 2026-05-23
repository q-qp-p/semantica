---
title: "Visualization Module"
description: "Interactive and static knowledge graph, ontology, embedding, and temporal visualization."
icon: "chart-bar"
---

`semantica.visualization` renders knowledge graphs, ontologies, embedding spaces, and temporal data as interactive HTML or static images — without launching the full Explorer server.

## What You Get

<CardGroup cols={2}>
  <Card title="GraphVisualizer" icon="diagram-project">
    Interactive HTML (PyVis) and static image (Matplotlib) graph rendering with layout options.
  </Card>
  <Card title="OntologyVisualizer" icon="sitemap">
    Class hierarchy and property relationship visualization from any OntologyManager.
  </Card>
  <Card title="EmbeddingVisualizer" icon="vector-square">
    UMAP, t-SNE, and PCA dimensionality reduction plots for embedding cluster analysis.
  </Card>
  <Card title="TemporalVisualizer" icon="clock">
    Timeline views, animated evolution, snapshot comparison, and temporal pattern highlights.
  </Card>
  <Card title="DistanceVisualizer (v0.5.0)" icon="circle-nodes">
    Ego-mode neighborhood views and N×N distance matrix heatmaps from Distance Intelligence.
  </Card>
  <Card title="AnalyticsVisualizer" icon="chart-bar">
    Centrality rankings, community-colored graphs, and degree distribution histograms.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Render a knowledge graph">
    ```python
    from semantica.visualization import GraphVisualizer

    viz = GraphVisualizer()

    # Interactive HTML — opens in browser, supports hover and click
    viz.visualize(graph, output="graph.html")
    ```
  </Step>
  <Step title="Apply layout and color options">
    ```python
    viz.visualize(
        graph,
        output="graph.html",
        layout="force_directed",   # "force_directed" | "hierarchical" | "circular" | "spring"
        node_color_by="type",      # color nodes by entity type attribute
        edge_label="relation",     # show edge relationship labels
        color_scheme="vibrant",    # color palette — see Color Schemes section
        max_nodes=500,             # limit rendering for large graphs
    )
    ```
  </Step>
  <Step title="Export to static formats">
    ```python
    # Static PNG — for reports and embedding in documents
    viz.visualize(graph, output="graph.png", dpi=150)

    # Vector SVG — for publications and scalable diagrams
    viz.visualize(graph, output="graph.svg")

    # PDF — for print or compliance reports
    viz.visualize(graph, output="graph.pdf")
    ```
  </Step>
</Steps>

## Visualizers

<Tabs>
  <Tab title="GraphVisualizer">
    Interactive and static knowledge graph rendering:

    ```python
    from semantica.visualization import GraphVisualizer

    viz = GraphVisualizer()

    # Interactive HTML
    viz.visualize(graph, output="graph.html")

    # Static PNG with custom DPI
    viz.visualize(graph, output="graph.png", backend="matplotlib", dpi=150)

    # Display inline (Jupyter or default browser)
    viz.show(graph)
    ```

    **Layout options:**

    | Layout | Description | Best For |
    | ------ | ----------- | -------- |
    | `force_directed` | Physics simulation — clusters emerge naturally | General graphs |
    | `hierarchical` | Top-down tree layout | Taxonomies, org charts |
    | `circular` | Nodes on a circle, edges as chords | Small dense graphs |
    | `spring` | Spring-force layout (Fruchterman-Reingold) | Medium graphs |
  </Tab>
  <Tab title="OntologyVisualizer">
    Visualize class hierarchies and property relationships:

    ```python
    from semantica.visualization import OntologyVisualizer

    viz = OntologyVisualizer()

    # Full ontology graph — classes, properties, and constraints
    viz.visualize(ontology, output="ontology.html")

    # Class hierarchy only — cleaner for large ontologies
    viz.visualize_hierarchy(ontology, output="hierarchy.html")
    ```
  </Tab>
  <Tab title="EmbeddingVisualizer">
    Project high-dimensional embeddings into 2D for cluster analysis:

    ```python
    from semantica.visualization import EmbeddingVisualizer

    viz = EmbeddingVisualizer()

    viz.visualize(
        embeddings=embeddings,
        labels=labels,
        output="embeddings.html",
        method="umap",    # "umap" | "tsne" | "pca"
    )
    ```

    | Method | Speed | Preserves | Best For |
    | ------ | ----- | --------- | -------- |
    | `umap` | Fast | Global + local structure | Large datasets, cluster discovery |
    | `tsne` | Medium | Local structure | Tight cluster separation |
    | `pca` | Very fast | Variance | Quick overview, linear structure |
  </Tab>
  <Tab title="TemporalVisualizer">
    Visualize how a knowledge graph changes over time:

    ```python
    from semantica.visualization import TemporalVisualizer
    from datetime import datetime

    viz = TemporalVisualizer()

    # Static timeline of additions and removals
    viz.visualize_timeline(temporal_kg, output="timeline.html")

    # Animated evolution — one frame per time step
    viz.animate(temporal_kg, output="evolution.html", fps=2)

    # Side-by-side snapshot comparison
    snap_a = temporal_kg.at(datetime(2020, 1, 1))
    snap_b = temporal_kg.at(datetime(2023, 1, 1))
    viz.compare_snapshots(snap_a, snap_b, output="snapshot_diff.html")

    # Pattern visualization — highlight recurring temporal patterns
    viz.visualize_patterns(temporal_kg, pattern_type="recurrence", output="patterns.html")
    ```
  </Tab>
  <Tab title="DistanceVisualizer (v0.5.0)">
    Semantic neighborhood and distance matrix visualization from Distance Intelligence:

    ```python
    from semantica.visualization import DistanceVisualizer

    viz = DistanceVisualizer()

    # Ego-mode: neighborhood of one node colored by distance band
    viz.visualize_ego(
        graph,
        center_node="Apple Inc.",
        output="ego.html",
        radius=0.5,    # semantic distance radius
    )

    # N×N distance matrix heatmap
    viz.visualize_distance_matrix(
        matrix=distance_matrix,
        labels=node_labels,
        output="distance_heatmap.html",
    )
    ```
  </Tab>
  <Tab title="AnalyticsVisualizer">
    Visualize graph analytics results — centrality, communities, and degree distribution:

    ```python
    from semantica.visualization import AnalyticsVisualizer
    from semantica.kg import CentralityCalculator, CommunityDetector

    calc       = CentralityCalculator()
    centrality = calc.calculate_all_centrality(kg)

    detector    = CommunityDetector()
    communities = detector.detect_communities(kg, algorithm="louvain")

    viz = AnalyticsVisualizer()

    # Bar chart of top-N nodes by centrality measure
    viz.visualize_centrality(centrality, metric="pagerank", top_k=20, output="centrality.html")

    # Community-colored graph
    viz.visualize_communities(kg, communities, output="communities.html")

    # Degree distribution histogram
    viz.visualize_degree_distribution(kg, output="degree_dist.html")

    # Combined analytics dashboard
    viz.visualize_analytics_dashboard(
        kg, centrality=centrality, communities=communities,
        output="analytics_dashboard.html",
    )
    ```
  </Tab>
</Tabs>

## Color Schemes

All visualizers accept a `color_scheme` parameter:

```python
viz.visualize(graph, output="graph.html", color_scheme="vibrant")
```

| Scheme | Description | Best For |
| ------ | ----------- | -------- |
| `default` | Blue-grey palette | General use |
| `vibrant` | High-contrast, saturated colours | Presentations |
| `pastel` | Soft, muted tones | Light backgrounds |
| `dark` | Dark background with bright nodes | Dark-mode dashboards |
| `light` | White background, thin edges | Publications, print |
| `colorblind` | Okabe-Ito safe palette | Accessibility |

## Export Formats

| Format | Interactive | Scalable | Best For |
| ------ | ----------- | -------- | -------- |
| `.html` | Yes | N/A | Web dashboards, exploratory analysis |
| `.png` | No | No | Reports, Jupyter notebooks |
| `.svg` | No | Yes | Publications, slide decks |
| `.pdf` | No | Yes | Print, compliance exports |

## Graph Explorer (Full Dashboard)

For a full browser-based UI with search, path finding, and the Ontology Hub, use `semantica.explorer`:

```python
from semantica.explorer import start_explorer

start_explorer(graph=kg, port=8080)
# Opens at http://localhost:8080
```

See the [Explorer reference](explorer) for the full feature set and REST API.

## Tips and Common Pitfalls

<Warning>
  **Use `max_nodes=500` for large graphs.** Force-directed layouts become unreadable and very slow above ~1,000 nodes. Limit with `max_nodes=500` or filter to a subgraph (e.g., top 100 nodes by PageRank) before visualizing.
</Warning>

<Tip>
  **HTML output is always the best starting point.** Interactive HTML lets you zoom, pan, hover for details, and hide node types — giving you orders of magnitude more exploratory power than a static PNG. Only export to PNG/SVG/PDF when embedding in a report.
</Tip>

<Tip>
  **Use `color_scheme="colorblind"` in publications and dashboards.** The Okabe-Ito palette is readable for everyone, including the ~8% of male readers who are red-green colorblind. Reserve `vibrant` for internal presentations only.
</Tip>

<Tip>
  **UMAP is faster than t-SNE at scale.** For embedding spaces with >5,000 points, UMAP completes in seconds; t-SNE may take minutes. Both produce good cluster separation — use UMAP for exploratory speed, t-SNE for final publication-quality plots.
</Tip>

<Warning>
  **`TemporalVisualizer.animate()` can produce large files.** Animated HTML files include all frames and can reach dozens of MB for long time series. Use `fps=1` or reduce the number of time steps for a manageable file size.
</Warning>

<Tip>
  **For interactive dashboards, prefer Explorer.** `GraphVisualizer.visualize()` generates a self-contained HTML file. `start_explorer()` gives a full live web app with search, filtering, path-finding, and REST API. Use Explorer for team exploration, Visualizer for standalone report embeds.
</Tip>

<CardGroup cols={2}>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being visualized.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Visualize ontology class structure.
  </Card>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Generate the embeddings visualized here.
  </Card>
  <Card title="Explorer" icon="globe" href="explorer">
    Full interactive Knowledge Explorer UI.
  </Card>
</CardGroup>
