---
title: "Learning More"
description: "Structured learning paths, configuration reference, troubleshooting, and performance guidance."
icon: "graduation-cap"
---

> Structured paths for going from beginner to production with Semantica.

---

## Learning Paths

<CardGroup cols={3}>
  <Card title="Beginner (1–2 hrs)" icon="seedling">
    New to Semantica and knowledge graphs.
    [Start with Installation](installation)
  </Card>
  <Card title="Intermediate (4–6 hrs)" icon="compass">
    Comfortable with basics, building production apps.
    [Start with Modules](modules)
  </Card>
  <Card title="Advanced (8+ hrs)" icon="rocket">
    Enterprise applications and customization.
    [Start with Architecture](architecture)
  </Card>
</CardGroup>

---

### Beginner Path

1. [Installation Guide](installation) — set up your environment
2. [Core Concepts](concepts) — understand KGs, embeddings, and extraction
3. [Getting Started](getting-started) — first working example
4. [Quickstart Tutorial](quickstart) — build your first KG
5. [Welcome to Semantica notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/01_Welcome_to_Semantica.ipynb) — interactive introduction

---

### Intermediate Path

1. [Modules Guide](modules) — every module with code examples
2. [Building Knowledge Graphs notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/07_Building_Knowledge_Graphs.ipynb)
3. [Embeddings notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/09_Embeddings.ipynb)
4. [GraphRAG Complete notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/use_cases/advanced_rag/01_GraphRAG_Complete.ipynb)
5. [Multi-Source Data Integration notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/06_Multi_Source_Data_Integration.ipynb)
6. [Use Cases](use-cases) — domain-specific examples

---

### Advanced Path

1. [Architecture Guide](architecture) — three-layer system overview
2. [Temporal Graphs notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/04_Temporal_Graphs.ipynb) — v0.4.0 temporal intelligence
3. [Ontology notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/14_Ontology.ipynb) — v0.5.0 Ontology Hub
4. [Complete Visualization Suite notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/03_Complete_Visualization_Suite.ipynb)
5. [Multi-Format Export notebook](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/05_Multi_Format_Export.ipynb)
6. [Deep Dive](deep-dive) — internals and extension points

---

## Configuration Reference

| Setting | Environment Variable | Default |
|---------|---------------------|---------|
| OpenAI API Key | `OPENAI_API_KEY` | `None` |
| Groq API Key | `GROQ_API_KEY` | `None` |
| Embedding Provider | `SEMANTICA_EMBEDDING_PROVIDER` | `"openai"` |
| Graph Backend | `SEMANTICA_GRAPH_BACKEND` | `"networkx"` |
| Log Level | `SEMANTICA_LOG_LEVEL` | `"INFO"` |
| Log Format | `SEMANTICA_LOG_FORMAT` | `"text"` |

---

## Troubleshooting

**`ModuleNotFoundError`**

Verify installation: `pip list | grep semantica`. Ensure Python 3.8+. For optional extras, install the relevant extra (e.g. `pip install "semantica[llm-openai]"`).

**`AuthenticationError`**

Set the relevant API key as an environment variable (`OPENAI_API_KEY`, `GROQ_API_KEY`, etc.). Never hardcode keys in source files.

**`MemoryError` or OOM crashes**

Reduce batch sizes or switch to a persistent graph backend (Neo4j, FalkorDB) instead of the default in-memory NetworkX backend.

Slow processing on large datasets — enable parallel processing via `Pipeline(workers=N)` and use GPU acceleration for embedding models.

**Windows `[all]` installation fails (v0.5.0 fix)**

Use `pip install "semantica[core]"` instead of `pip install "semantica[all]"` on Windows. See the [Installation guide](installation) for the full list of extras.

cp1252 encoding crash on Windows (v0.5.0 fix) — pass `encoding="utf-8"` explicitly to `FileIngestor` or set `PYTHONIOENCODING=utf-8` in your environment.

---

## Performance Optimization

**Batch processing** — process documents in batches rather than one at a time; configure chunk sizes based on available RAM.

**Parallel execution** — `Pipeline(workers=N)` runs extraction steps in parallel across documents.

**Backend selection:**

| Operation | NetworkX | Neo4j / FalkorDB |
|-----------|----------|-----------------|
| Graph construction | Fast | Moderate |
| Query performance | Moderate | Fast |
| Scalability | Low (in-memory) | High (persistent) |

Use NetworkX for development and small graphs; switch to a persistent backend for production.

---

## Security Best Practices

**API keys** — store in environment variables or a secrets manager; never commit them to version control; rotate regularly.

**Data privacy** — use local embedding models (Ollama, HuggingFace) for sensitive data; avoid sending PII to external APIs without appropriate data handling agreements.

**Exports** — encrypt sensitive graph exports at rest; use the v0.5.0 SSRF-safe `base_url` validation when configuring custom LLM gateways.

---

## See Also

<CardGroup cols={2}>
  <Card title="Cookbook" icon="book-open" href="cookbook">
    Interactive Jupyter notebook tutorials.
  </Card>
  <Card title="FAQ" icon="circle-question" href="faq">
    Common questions answered.
  </Card>
  <Card title="API Reference" icon="code" href="reference/core">
    Complete technical documentation.
  </Card>
  <Card title="Use Cases" icon="briefcase" href="use-cases">
    Real-world domain examples.
  </Card>
</CardGroup>
