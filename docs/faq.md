---
title: "FAQ"
description: "Common questions about Semantica — installation, features, integrations, and troubleshooting."
icon: "circle-question"
---

<AccordionGroup>

## General

<Accordion title="What is Semantica?" icon="info-circle">
Semantica is an open-source framework for building context graphs and decision intelligence layers for AI. It transforms unstructured data — documents, APIs, databases — into structured knowledge graphs with full provenance tracking, making AI systems explainable and auditable.
</Accordion>

<Accordion title="What can I build with Semantica?" icon="hammer">

- Knowledge graphs from documents and multi-source data
- GraphRAG systems with graph-grounded retrieval
- AI agents with structured decision history and semantic memory
- Compliance-ready pipelines with W3C PROV-O lineage

</Accordion>

<Accordion title="What makes Semantica different from LangChain or LlamaIndex?" icon="scale-balanced">
Most frameworks stop at retrieval or generation. Semantica adds an **accountability layer**: every decision is recorded, every fact links to a source, and every reasoning step is explainable. It's designed for environments where you need to audit *why* an AI reached a conclusion — not just what it said.
</Accordion>

<Accordion title="Is Semantica free?" icon="tag">
Yes — MIT licensed, no vendor lock-in. Some features require third-party API keys (e.g., OpenAI embeddings), but Semantica itself is always free.
</Accordion>

<Accordion title="What's the latest version?" icon="star">

**v0.5.0** — released May 2026. Highlights: Ontology Hub, Distance Intelligence, Parquet/XML ingestion, 12 security fixes, Graph Explorer redesign.

```bash
pip install --upgrade semantica
```

</Accordion>

</AccordionGroup>

---

<AccordionGroup>

## Installation

<Accordion title="How do I install Semantica?" icon="download">

```bash
pip install semantica
```

See [Installation](installation) for virtual environment setup, optional extras (`[gpu]`, `[all]`, provider-specific), and troubleshooting.
</Accordion>

<Accordion title="What Python version do I need?" icon="python">
Python **3.8 or higher**. Python 3.11+ is recommended for best performance.
</Accordion>

<Accordion title="The [all] extra fails on Windows" icon="windows">
This was a known bug — fixed in **v0.5.0**. Upgrade:

```bash
pip install --upgrade semantica
```
</Accordion>

<Accordion title="What are the system requirements?" icon="server">

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.11+ |
| RAM | 4 GB | 16 GB+ |
| GPU | Optional | CUDA for embeddings / ML |

</Accordion>

</AccordionGroup>

---

<AccordionGroup>

## Data & Features

<Accordion title="What data sources does Semantica support?" icon="database">

| Category | Sources |
|----------|---------|
| **Files** | PDF, DOCX, HTML, JSON, CSV, Excel, PPTX, Parquet (v0.5.0), XML (v0.5.0), archives |
| **Web** | `WebIngestor` crawl, RSS feeds |
| **Databases** | PostgreSQL, MySQL, Snowflake via `DBIngestor` / `SnowflakeIngestor` |
| **Streams** | Kafka, real-time ingestion |
| **Protocols** | MCP (Model Context Protocol) |

</Accordion>

<Accordion title="Can I use my own models?" icon="robot">
Yes. Semantica supports custom entity extraction models, embedding models, LLM providers via LiteLLM (100+ models), and custom pipeline processors via the `PluginRegistry`.
</Accordion>

<Accordion title="Does Semantica support GPUs?" icon="bolt">
Yes. When available, GPUs are used automatically for embedding generation, ML model inference, and vector operations.

```bash
pip install "semantica[gpu]"
```
</Accordion>

<Accordion title="How does Semantica handle large datasets?" icon="layer-group">

- **Batching** — process documents in configurable chunks
- **Parallel processing** — `Pipeline` supports configurable worker counts
- **Delta processing** — update graphs incrementally without full recompute
- **Graph backends** — swap in-memory NetworkX for Neo4j, FalkorDB, or Apache AGE at scale

</Accordion>

<Accordion title="What is Temporal Intelligence? (v0.4.0)" icon="clock">
`TemporalKnowledgeGraph` attaches `valid_from`/`valid_until` to nodes and edges. Supports point-in-time queries, all 13 Allen interval algebra relations, and OWL-Time export.

```python
from semantica.kg import TemporalKnowledgeGraph

tkg = TemporalKnowledgeGraph()
tkg.add_temporal_triple("A", "caused", "B", valid_from="2024-01", valid_until="2024-06")
snapshot = tkg.query_at_time("2024-03")
```
</Accordion>

<Accordion title="What is the Ontology Hub? (v0.5.0)" icon="sitemap">
A visual browser UI for the full ontology lifecycle — visual editor, SHACL Studio, alignment authoring, health dashboard, and version control. Launch via `semantica.explorer`.
</Accordion>

<Accordion title="What is Distance Intelligence? (v0.5.0)" icon="compass">
Semantic neighborhood exploration for any graph node: N×N distance matrices, ego-mode visualization, distance band classification (`near`/`mid`/`far`), and embedding cache optimization.
</Accordion>

<Accordion title="My NER extractor silently falls back to pattern mode on a custom gateway" icon="triangle-exclamation">
Fixed in **v0.5.0**. The `response_format=json_object` parameter is now conditionally omitted for incompatible gateways, and a plain `generate()` + JSON parsing fallback is used automatically. Upgrade to fix.
</Accordion>

</AccordionGroup>

---

<AccordionGroup>

## Technical

<Accordion title="What graph databases are supported?" icon="diagram-project">
Neo4j, FalkorDB, Apache AGE (PostgreSQL), Amazon Neptune, and in-memory NetworkX for development.
</Accordion>

<Accordion title="What export formats are available?" icon="file-export">
RDF (Turtle, JSON-LD, N-Triples, XML), Apache Parquet, ArangoDB AQL, CSV, YAML, and OWL ontologies.
</Accordion>

<Accordion title="What vector stores are supported?" icon="server">
FAISS, Pinecone, Weaviate, Qdrant, Milvus, PgVector, and in-memory.
</Accordion>

<Accordion title="What LLM providers are supported?" icon="microchip">
Groq, OpenAI, Anthropic, Google Gemini, Ollama (local), DeepSeek, Novita AI, LiteLLM (100+ models), and any OpenAI-compatible gateway.
</Accordion>

<Accordion title="Is Semantica production-ready?" icon="shield-check">
Yes. v0.5.0 ships with:

- 1,000+ passing tests
- `PipelineValidator` and `FailureHandler` with exponential backoff
- W3C PROV-O provenance tracking
- Change management with SHA-256 checksums
- 12 security vulnerability fixes (eval injection, pickle deserialization, SQL injection, XXE, SSRF, ReDoS, path traversal, and more)
</Accordion>

</AccordionGroup>

---

<AccordionGroup>

## Troubleshooting

<Accordion title="ModuleNotFoundError: No module named 'semantica'" icon="xmark-circle">
Ensure you have the correct Python environment active:

```bash
pip list | grep semantica
pip install --upgrade semantica
```
</Accordion>

<Accordion title="Installation fails with dependency errors" icon="xmark-circle">

```bash
pip install --upgrade pip wheel
pip install semantica
```
</Accordion>

<Accordion title="Memory errors during processing" icon="memory">
Reduce batch sizes, enable streaming ingestion, or switch to a persistent graph backend (Neo4j, FalkorDB).
</Accordion>

<Accordion title="Slow embedding or inference" icon="gauge-high">
Install GPU support and ensure CUDA is available:

```bash
pip install "semantica[gpu]"
```
</Accordion>

<Accordion title="Unicode / cp1252 crash on Windows" icon="windows">
Fixed in **v0.5.0**. Upgrade:

```bash
pip install --upgrade semantica
```
</Accordion>

</AccordionGroup>

---

## Support

<CardGroup cols={3}>
  <Card title="Discord" icon="discord" href="https://discord.gg/sV34vps5hH">
    Community chat and live support.
  </Card>
  <Card title="GitHub Issues" icon="github" href="https://github.com/semantica-agi/semantica/issues">
    Bug reports and feature requests.
  </Card>
  <Card title="Contributing" icon="code-pull-request" href="contributing">
    Help improve Semantica.
  </Card>
</CardGroup>
