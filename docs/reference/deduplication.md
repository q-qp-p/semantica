---
title: "Deduplication Module"
description: "Entity deduplication v1/v2 — similarity scoring, blocking, merging, and cluster-based batch processing."
icon: "copy"
---

`semantica.deduplication` detects and merges duplicate entities across sources to produce a clean, single-source-of-truth knowledge graph. **v2 strategies** (`blocking_v2`, `hybrid_v2`, `semantic_v2`) are up to **7x faster** than v1 with fine-grained result control.

## Why Deduplicate?

Real-world data sources disagree on names. "Apple Inc.", "Apple Computer", and "Apple International Ltd" can all refer to the same company — but if they land in your knowledge graph as separate nodes, every query that should return one entity returns three. Relationships, analytics, and retrieval all degrade.

Deduplication solves this before it reaches the graph:

- **Cross-source ingestion** — Wikipedia calls it "OpenAI", SEC filings call it "OpenAI, Inc.", your CRM calls it "OpenAI LLC"
- **Data entry variation** — "Steve Jobs", "Steven P. Jobs", "S. Jobs" are the same person
- **Transliteration differences** — Cyrillic, Chinese, or Arabic names romanized inconsistently across sources
- **Abbreviation drift** — "US", "U.S.", "United States", "USA" all mean the same thing

## What You Get

<CardGroup cols={2}>
  <Card title="DuplicateDetector" icon="copy">
    Pairwise and batch duplicate detection with configurable strategies and result filtering.
  </Card>
  <Card title="EntityMerger" icon="code-merge">
    Merge duplicate groups with configurable property-level merge policies.
  </Card>
  <Card title="SimilarityCalculator" icon="chart-line">
    Multi-factor similarity: Levenshtein, Jaro-Winkler, cosine, Jaccard, and embedding.
  </Card>
  <Card title="ClusterBuilder" icon="diagram-project">
    Union-Find and hierarchical clustering for large-scale batch deduplication.
  </Card>
  <Card title="MergeStrategyManager" icon="sliders">
    Reusable per-property merge rule configurations — define once, apply across operations.
  </Card>
  <Card title="v2 Strategies" icon="bolt">
    `blocking_v2`, `hybrid_v2`, `semantic_v2` — up to 7x faster than v1 equivalents.
  </Card>
</CardGroup>

## Quick Start

```python
from semantica.deduplication import detect_duplicates, merge_entities

# Detect
duplicates = detect_duplicates(entities, method="hybrid_v2", similarity_threshold=0.85)

# Merge
merged = merge_entities(entities, duplicates, method="keep_most_complete")
print(f"Reduced {len(entities)} → {len(merged)} entities")
```

## Choosing a Strategy

<Tabs>
  <Tab title="hybrid_v2 (recommended)">
    Combines blocking + string similarity + semantic embedding — best default for production:

    ```python
    from semantica.deduplication import DuplicateDetector

    detector   = DuplicateDetector(similarity_threshold=0.85)
    duplicates = detector.detect_duplicates(entities, strategy="hybrid_v2")
    ```

    Best for: general production use — handles 95% of real-world cases without GPU. Catches string variants ("Apple Inc." / "Apple Inc") and semantic aliases ("Machine Learning" / "ML").
  </Tab>
  <Tab title="semantic_v2">
    Pure embedding-based similarity — highest accuracy for cross-language and abbreviation matching:

    ```python
    detector   = DuplicateDetector(similarity_threshold=0.85)
    duplicates = detector.detect_duplicates(entities, strategy="semantic_v2")
    ```

    Best for: entities that use different words for the same concept ("ML" vs "Machine Learning"), cross-language entity matching, and abbreviation expansion. Requires embedding model.
  </Tab>
  <Tab title="blocking_v2">
    Blocking + Jaro-Winkler string similarity only — fastest option for CPU-only environments:

    ```python
    detector   = DuplicateDetector(similarity_threshold=0.85)
    duplicates = detector.detect_duplicates(entities, strategy="blocking_v2")
    ```

    Best for: large datasets (500K+ entities) where speed is critical and entities are in the same language. No GPU required.
  </Tab>
  <Tab title="Strategy Comparison">

    | Strategy | Algorithm | Speed | Accuracy | Best For |
    | -------- | --------- | ----- | -------- | -------- |
    | `jaro_winkler` | String similarity only (v1) | Fast | Medium | Small datasets, names, single-source |
    | `blocking_v2` | Blocking + Jaro-Winkler | Very fast | Medium | Large datasets, speed-critical, CPU-only |
    | `hybrid_v2` | Blocking + string + semantic | Fast | High | General production use — best default |
    | `semantic_v2` | Embedding similarity | Medium | Highest | Semantic aliases, cross-language, abbreviations |

    **Rules of thumb:**
    - Start with `hybrid_v2` — it handles 95% of real-world cases without GPU
    - Use `semantic_v2` when entities use different words for the same concept
    - Use `blocking_v2` when processing >500k entities and speed matters most
    - Never use v1 strategies on new projects — they exist for backwards compatibility only
  </Tab>
</Tabs>

### Threshold Tuning

| Domain | Recommended Threshold | Notes |
| ------ | --------------------- | ----- |
| Person names | 0.85–0.90 | Names vary a lot; too high misses "Steve" / "Steven" |
| Organization names | 0.80–0.88 | Corporate suffixes create variation; lower threshold helps |
| Product names | 0.88–0.95 | Product names are more stable |
| Medical terms | 0.90–0.95 | High precision required; false merges are dangerous |
| General entities | 0.85 | Safe default starting point |

Start at 0.85, inspect false positives and false negatives, then adjust ±0.05.

## DuplicateDetector

<Note>
  **v0.5.0 fix:** `DuplicateDetector` no longer produces duplicate definition errors when the same entity appears in multiple sources with identical definitions.
</Note>

```python
from semantica.deduplication import DuplicateDetector

detector   = DuplicateDetector(similarity_threshold=0.85)
duplicates = detector.detect_duplicates(entities)

for dup in duplicates:
    print(f"{dup.entity_a} ≈ {dup.entity_b}  ({dup.similarity:.2f})")
```

Fine-grained control over strategy, thresholds, and result size:

```python
duplicates = detector.detect_duplicates(
    entities,
    strategy="hybrid_v2",
    min_similarity=0.85,
    top_k_per_entity=3,     # max candidates per entity — avoids false-positive floods
    max_results=100,
    sort_by="similarity",   # "similarity" | "entity_id" | "cluster_size"
)
```

**Key behaviours:**
- Defaults to `hybrid_v2` when no strategy is specified
- `top_k_per_entity=3` prevents one entity from flooding results by being a near-match to everything
- Pairs are returned once — never both `(A, B)` and `(B, A)`
- `sort_by="similarity"` puts highest-confidence duplicates first for faster manual review

## EntityMerger

Merge detected duplicate groups into canonical entities, preserving provenance:

```python
from semantica.deduplication import EntityMerger

merger = EntityMerger()
merged_entities = merger.merge_duplicates(
    entities,
    strategy="keep_most_complete",
    preserve_provenance=True,
)

print(f"Merged to: {len(merged_entities)} canonical entities")
```

### Merge Strategies

| Strategy | Behavior | When to Use |
| -------- | -------- | ----------- |
| `keep_first` | Keep the first entity in each group | Source order is meaningful (most authoritative first) |
| `keep_last` | Keep the most recently seen entity | Most recent source is most accurate |
| `keep_most_complete` | Keep the entity with the most non-null properties | Default — maximizes data richness |
| `keep_highest_confidence` | Keep the entity with the highest confidence score | Extraction pipelines produce confidence scores |
| `merge_all` | Merge all properties; combine non-conflicting fields | You want every known alias, tag, and label |

### Per-Property Merge Rules

Use `MergeStrategyManager` to apply different `MergeStrategy` values per property:

```python
from semantica.deduplication import MergeStrategyManager, MergeStrategy

manager = MergeStrategyManager()
manager.add_property_rule("name",       MergeStrategy.KEEP_FIRST)
manager.add_property_rule("aliases",    MergeStrategy.MERGE_ALL)
manager.add_property_rule("confidence", MergeStrategy.KEEP_HIGHEST_CONFIDENCE)
manager.add_property_rule("created_at", MergeStrategy.KEEP_FIRST)
manager.add_property_rule("updated_at", MergeStrategy.KEEP_LAST)

merged_entity = manager.merge_entities(duplicate_group)
```

| Strategy | Behaviour |
| -------- | --------- |
| `KEEP_FIRST` | Value from the first entity in the group |
| `KEEP_LAST` | Value from the last entity |
| `KEEP_MOST_COMPLETE` | Entity with the most non-null fields |
| `KEEP_HIGHEST_CONFIDENCE` | Entity with the highest confidence score |
| `MERGE_ALL` | Combine all properties from every entity in the group |

## SimilarityCalculator

Compute multi-factor similarity scores — useful for debugging why two entities were (or were not) detected as duplicates:

```python
from semantica.deduplication import SimilarityCalculator

calc  = SimilarityCalculator()
score = calc.calculate_similarity(entity_a, entity_b)

print(score.score)                    # overall score 0.0–1.0
print(score.components["label"])      # label similarity contribution
print(score.components["embedding"])  # semantic similarity contribution
print(score.components["property"])   # property overlap contribution

lev  = calc.levenshtein("Apple Inc.", "Apple Inc")
jaro = calc.jaro_winkler("Steve Jobs", "Steven Jobs")
cos  = calc.cosine_similarity(embedding_a, embedding_b)
jacc = calc.jaccard({"founded", "tech"}, {"founded", "technology"})
```

## ClusterBuilder

Build entity clusters for large-scale batch deduplication:

```python
from semantica.deduplication import ClusterBuilder

builder = ClusterBuilder(algorithm="union_find")   # or "hierarchical"
result  = builder.build_clusters(entities, similarity_threshold=0.85)

print(f"Original:   {len(entities)} entities")
print(f"Clusters:   {len(result.clusters)} groups")
print(f"Singletons: {result.singleton_count}")

for cluster in result.clusters:
    print(f"  [{cluster.id}] members={cluster.members}  cohesion={cluster.cohesion:.2f}")
```

### Union-Find vs Hierarchical

```python
# Union-Find — O(n·α(n)), scales to millions; use for production
builder = ClusterBuilder(algorithm="union_find")

# Hierarchical — tighter clusters; use when quality matters more than speed
builder = ClusterBuilder(algorithm="hierarchical", linkage="average")
result  = builder.build_clusters(entities, similarity_threshold=0.85)
```

**Key behaviours:**
- Union-Find groups entities transitively: if A≈B and B≈C, all three land in one cluster even if A and C are only 0.70 similar
- Hierarchical with `linkage="average"` avoids chaining by requiring average similarity across all pairs to meet the threshold

### Cluster Quality Metrics

```python
print(f"Silhouette score: {result.quality.silhouette_score:.3f}")
# → -1.0 to 1.0; above 0.5 is good, above 0.7 is excellent

print(f"Avg cohesion:     {result.quality.avg_cohesion:.3f}")
print(f"Avg separation:   {result.quality.avg_separation:.3f}")
```

## MergeStrategyManager

Define complex, reusable merge configurations once and apply them across multiple operations:

```python
from semantica.deduplication import MergeStrategyManager, MergeStrategy

manager = MergeStrategyManager()
manager.add_property_rule("name",        MergeStrategy.KEEP_FIRST)
manager.add_property_rule("aliases",     MergeStrategy.MERGE_ALL)
manager.add_property_rule("description", MergeStrategy.KEEP_MOST_COMPLETE)
manager.add_property_rule("confidence",  MergeStrategy.KEEP_HIGHEST_CONFIDENCE)
manager.add_property_rule("sources",     MergeStrategy.MERGE_ALL)
manager.add_property_rule("created_at",  MergeStrategy.KEEP_FIRST)
manager.add_property_rule("updated_at",  MergeStrategy.KEEP_LAST)

merged_entity = manager.merge_entities(duplicate_group)
```

## Blocking Strategies

```python
detector = DuplicateDetector(
    blocking_strategy="token",       # "token" | "phonetic" | "ngram"
    blocking_threshold=0.6,
    similarity_threshold=0.85
)
```

| Blocking Strategy | How It Works | Best For |
| ----------------- | ------------ | -------- |
| `token` | Shared token overlap (default) | General entity names |
| `phonetic` | Soundex/Metaphone phonetic codes | Names with spelling variations |
| `ngram` | Character n-gram overlap | Short strings, typos |

## Custom Similarity Functions

```python
from semantica.deduplication import method_registry

def drug_name_similarity(entity_a, entity_b) -> float:
    compound_a = entity_a.properties.get("active_compound", "")
    compound_b = entity_b.properties.get("active_compound", "")
    return 1.0 if compound_a == compound_b else 0.0

method_registry.register("similarity", "drug_name", drug_name_similarity)

detector = DuplicateDetector(similarity_method="drug_name", similarity_threshold=0.90)
```

## Schemas

<AccordionGroup>
  <Accordion title="Cluster and ClusterResult schemas">

```python
@dataclass
class Cluster:
    id:        str
    members:   List[str]   # entity IDs in this duplicate group
    cohesion:  float       # mean pairwise similarity within the cluster (0–1)
    centroid:  str         # member ID closest to the cluster centroid

@dataclass
class ClusterResult:
    clusters:         List[Cluster]
    singleton_count:  int            # entities with no duplicates found
    merge_candidates: int            # clusters with > 1 member
    quality:          ClusterQuality
```

  </Accordion>
  <Accordion title="ClusterQuality schema">

```python
@dataclass
class ClusterQuality:
    silhouette_score:  float   # -1 to 1; above 0.5 is good
    avg_cohesion:      float   # mean within-cluster similarity
    avg_separation:    float   # mean between-cluster distance
```

  </Accordion>
</AccordionGroup>

## End-to-End Pipeline

<Steps>
  <Step title="Load entities from multiple sources">
    ```python
    entities = load_entities_from_sources(["crunchbase", "wikipedia", "internal_db"])
    print(f"Loaded: {len(entities)} raw entities")
    ```
  </Step>
  <Step title="Detect duplicate pairs">
    ```python
    from semantica.deduplication import DuplicateDetector

    detector   = DuplicateDetector(similarity_threshold=0.85)
    duplicates = detector.detect_duplicates(entities, strategy="hybrid_v2")
    print(f"Found: {len(duplicates)} duplicate pairs")
    ```
  </Step>
  <Step title="Configure property-level merge rules">
    ```python
    from semantica.deduplication import MergeStrategyManager, MergeStrategy

    manager = MergeStrategyManager()
    manager.add_property_rule("name",        MergeStrategy.KEEP_FIRST)
    manager.add_property_rule("aliases",     MergeStrategy.MERGE_ALL)
    manager.add_property_rule("description", MergeStrategy.KEEP_MOST_COMPLETE)
    ```
  </Step>
  <Step title="Merge and inspect results">
    ```python
    from semantica.deduplication import EntityMerger

    merger = EntityMerger()
    merged = merger.merge_duplicates(entities, preserve_provenance=True)
    print(f"Result: {len(merged)} canonical entities")

    for entity in merged:
        if hasattr(entity, "source_entities"):
            print(f"{entity.label} merged from: {entity.source_entities}")
    ```
  </Step>
</Steps>

## Tips and Common Pitfalls

<Warning>
  **Normalize before deduplicating.** Run `TextNormalizer` and `EntityNormalizer` first. "APPLE INC." and "apple inc." will score 0.50 on string similarity but 1.0 after case normalization. See the [Normalize](normalize) module.
</Warning>

<Tip>
  **Too many false positives?** Raise `similarity_threshold` by 0.05 or switch from `blocking_v2` to `hybrid_v2` to add semantic precision on top of string matching.
</Tip>

<Tip>
  **Too many missed duplicates?** Lower `similarity_threshold` by 0.05, or switch to `semantic_v2` to catch entities that use different words ("ML" vs "Machine Learning").
</Tip>

<Warning>
  **Union-Find over-merges?** The transitive grouping means weak chains can connect unrelated entities. Switch to `hierarchical` clustering with `linkage="average"` to require that every pair within a cluster meets the threshold — not just a chain of nearby pairs.
</Warning>

<Tip>
  **Preserve provenance on merge.** Set `preserve_provenance=True` so you can always trace which source contributed each property to the merged entity. Critical for audit and debugging.
</Tip>

<Tip>
  **Inspect similarity components.** When a pair is flagged and you're not sure why, use `SimilarityCalculator.calculate_similarity()` to see the per-component breakdown (`label`, `embedding`, `property`) and identify which factor is driving the match.
</Tip>

<Warning>
  **Don't deduplicate after building the graph.** Deduplicate entities *before* `GraphBuilder` ingests them. Merging inside a live graph is possible but requires tracking and rewriting all relationship endpoints.
</Warning>

<CardGroup cols={2}>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Detect value conflicts between non-duplicate entities.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    GraphBuilder uses deduplication during construction.
  </Card>
  <Card title="Normalize" icon="broom" href="normalize">
    Normalize entity names before deduplication for better accuracy.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Track merged entity lineage and source attribution.
  </Card>
</CardGroup>
