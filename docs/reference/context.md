---
title: "Context Module"
description: "Agent context graphs, decision tracking, causal chains, precedent search, and policy enforcement."
icon: "brain"
---

`semantica.context` is the memory and decision layer for AI agents. It stores facts with provenance, records decisions as first-class objects with causal chains, and lets agents search their own history to stay consistent across runs.

## What You Get

<CardGroup cols={2}>
  <Card title="AgentContext" icon="brain">
    Unified interface for memory, decision tracking, and graph-backed retrieval.
  </Card>
  <Card title="ContextGraph" icon="diagram-project">
    Persistent knowledge graph with centrality analysis, community detection, and decision management.
  </Card>
  <Card title="AgentMemory" icon="database">
    Embedding-backed memory with TTL, tagging, and importance scoring.
  </Card>
  <Card title="DecisionRecorder" icon="list-check">
    Records decisions with causal chains, confidence scores, and outcome tracking.
  </Card>
  <Card title="PolicyEngine" icon="shield-check">
    Validates decisions against configurable rules before they're recorded.
  </Card>
  <Card title="EntityLinker" icon="link">
    Maps entity mentions to canonical URIs — prevents "Apple", "Apple Inc.", and "AAPL" from becoming three separate nodes.
  </Card>
</CardGroup>

<img src="/assets/img/diagrams/agent-context-flow.svg" alt="AgentContext hub: AI Agent calls store/retrieve against VectorStore and record_decision against ContextGraph" style={{ width: '100%', borderRadius: '12px', margin: '0 0 24px' }} />

## Quick Start

<Steps>
  <Step title="Initialize the agent context">
    ```python
    from semantica.context import AgentContext, ContextGraph
    from semantica.vector_store import VectorStore

    context = AgentContext(
        vector_store=VectorStore(backend="faiss", dimension=768, index_path="context.faiss"),
        knowledge_graph=ContextGraph(advanced_analytics=True),
        decision_tracking=True,
    )
    ```
  </Step>
  <Step title="Store facts and retrieve by semantic similarity">
    ```python
    memory_id = context.store(
        "GPT-4 outperforms GPT-3.5 on reasoning benchmarks by 40%",
        metadata={"source": "openai_blog", "date": "2024-01"}
    )

    results = context.retrieve("LLM benchmark comparisons", top_k=5)
    for r in results:
        print(f"{r['content']}  (score: {r['score']:.3f})")
    ```
  </Step>
  <Step title="Record decisions with full provenance">
    ```python
    decision_id = context.record_decision(
        category="model_selection",
        scenario="Choose LLM for production reasoning pipeline",
        reasoning="GPT-4 benchmark advantage justifies 3x cost increase",
        outcome="selected_gpt4",
        confidence=0.91,
    )
    ```
  </Step>
  <Step title="Find precedents before new decisions">
    ```python
    # Search past decisions — prevents contradictory choices across runs
    precedents = context.find_precedents("model selection reasoning", limit=5)

    for p in precedents:
        print(f"[{p.category}] {p.outcome}  (similarity: {p.similarity:.2f})")
        print(f"  Reasoning: {p.reasoning}")

    # Analyze downstream impact of a past decision
    influence = context.analyze_decision_influence(decision_id)
    print(f"Decisions influenced: {len(influence.downstream_decisions)}")
    ```
  </Step>
</Steps>

## AgentContext

The main entry point. Wraps memory, graph, and decision tracking behind a single API.

### Constructor Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `vector_store` | `VectorStore` | required | Backend for embedding-based memory retrieval |
| `knowledge_graph` | `ContextGraph` | `None` | Enables graph-backed relationships and analytics |
| `decision_tracking` | `bool` | `False` | Activates `DecisionRecorder` for every decision |
| `graph_expansion` | `bool` | `True` | Auto-expands graph from stored memories |
| `advanced_analytics` | `bool` | `True` | Enables centrality and community analysis |
| `kg_algorithms` | `bool` | `True` | Adds path-finding and link prediction |

### Core Methods

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `store(content, metadata)` | `str` (memory_id) | Embed and store a fact |
| `retrieve(query, top_k)` | `List[Dict]` | Semantic similarity search |
| `record_decision(category, scenario, reasoning, outcome, confidence)` | `str` (decision_id) | Record a decision with full provenance |
| `find_precedents(scenario, category, limit)` | `List[Decision]` | Find similar past decisions |
| `analyze_decision_influence(decision_id)` | `InfluenceResult` | Trace downstream impact |
| `query_with_reasoning(query, llm_provider, max_hops)` | `Dict` | GraphRAG with multi-hop traversal |
| `get_context_insights()` | `Dict` | Analytics summary |

### Multi-Hop GraphRAG

```python
from semantica.llms import Groq

llm    = Groq(model="llama-3.3-70b-versatile")
result = context.query_with_reasoning(
    query="What technologies have we chosen and why?",
    llm_provider=llm,
    max_hops=2,
)

print(result["response"])
for step in result["reasoning_path"]:
    print(f"  {step}")
```

## ContextGraph

The knowledge graph backing `AgentContext`. Can be used standalone for relationship modelling.

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)

graph.add_node("Python",  "language",  properties={"paradigm": "multi-paradigm"})
graph.add_node("FastAPI", "framework", properties={"language": "Python"})
graph.add_edge("Python", "FastAPI", "enables")

decision_id = graph.add_decision_simple(
    category="technology_choice",
    scenario="Web API framework selection",
    reasoning="FastAPI's async support and auto-docs match our requirements",
    outcome="selected_fastapi",
    confidence=0.92,
    entities=["Python", "FastAPI"],
)

similar = graph.find_precedents_by_scenario("web framework", limit=3)
impact  = graph.analyze_decision_impact(decision_id)
chain   = graph.trace_decision_chain(decision_id)
```

### ContextGraph Constructor Options

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `advanced_analytics` | `bool` | `False` | PageRank, betweenness centrality |
| `centrality_analysis` | `bool` | `False` | Full centrality suite |
| `community_detection` | `bool` | `False` | Louvain community clustering |
| `node_embeddings` | `bool` | `False` | Node2Vec embeddings for structural similarity |

### ContextGraph — Full Method Reference

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `add_node(id, label, properties)` | `None` | Add a node to the context graph |
| `add_edge(source, target, rel_type, properties)` | `None` | Add a directed edge |
| `query_neighbors(node_id, depth)` | `List[ContextNode]` | BFS neighbors up to given depth |
| `record_decision(...)` | `str` (decision_id) | Add decision node with causal edges |
| `find_precedents(category, limit)` | `List[Decision]` | Recent decisions in this category |
| `find_precedents_by_scenario(scenario, limit)` | `List[Decision]` | Semantically similar past scenarios |
| `analyze_decision_impact(decision_id)` | `Dict` | Downstream nodes influenced |
| `trace_decision_chain(decision_id)` | `CausalChain` | Full causality tree |
| `get_decision_insights()` | `Dict` | Aggregate stats across all decisions |
| `trace_decision_causality(decision_id)` | `CausalChain` | Alias for `trace_decision_chain` |

## AgentMemory (Low-Level)

For fine-grained control over memory storage, TTL, and importance scoring:

```python
from semantica.context import AgentMemory
from semantica.vector_store import VectorStore

memory = AgentMemory(
    vector_store=VectorStore(backend="faiss", dimension=768),
    capacity=10_000,       # max memories before oldest are evicted
    ttl_days=90,           # memories older than this are auto-expired (None = never)
)

memory_id = memory.store(
    "Critical compliance rule: all trades must be pre-approved",
    importance=0.95,
    tags=["compliance", "trading"],
)

results = memory.retrieve(
    query="trade approval requirements",
    top_k=5,
    min_importance=0.5,
    tags=["compliance"],
)

memory.update(memory_id, importance=1.0)
memory.forget(memory_id)
all_memories = memory.get_all()
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `vector_store` | `VectorStore` | required | Embedding backend for semantic retrieval |
| `capacity` | `int` | `1000` | Max items before LRU eviction |
| `ttl_days` | `Optional[int]` | `None` | Days before automatic expiry; `None` = keep forever |

## PolicyEngine

Validate decisions against configurable rules before they're committed:

```python
from semantica.context import PolicyEngine

policy = PolicyEngine()
policy.add_rule("confidence_threshold", lambda d: d.confidence >= 0.7)
policy.add_rule("requires_reasoning",   lambda d: len(d.reasoning) >= 20)

is_valid, violations = policy.validate(decision_data)

if is_valid:
    context.record_decision(**decision_data)
else:
    # Create approval chain for manual review
    chain = policy.create_approval_chain(
        decision_data,
        approvers=["manager@company.com", "compliance@company.com"],
    )
    print(f"Approval chain created: {chain.chain_id}")
```

## EntityLinker

Maps extracted entity mentions to canonical URIs — essential for cross-document entity resolution:

```python
from semantica.context import EntityLinker

linker = EntityLinker()

entities = [
    {"text": "Apple Inc.", "type": "ORGANIZATION"},
    {"text": "Apple",      "type": "ORGANIZATION"},
    {"text": "AAPL",       "type": "ORGANIZATION"},
]
linked = linker.link_entities(entities, sources=["reuters", "sec_filings"])

for e in linked:
    print(f"{e.text} → {e.canonical_form}  ({e.uri})")
    print(f"  confidence: {e.confidence:.2f}, sources: {e.sources}")
```

## ContextRetriever

Hybrid retrieval combining vector similarity, graph traversal, and memory — gives richer context than pure vector search:

```python
from semantica.context import ContextRetriever

retriever = ContextRetriever(
    vector_store=vector_store,
    context_graph=context_graph,
    agent_memory=memory,
)

results = retriever.retrieve(
    query="What decisions were made about cloud infrastructure?",
    top_k=10,
    vector_weight=0.5,    # weight of vector similarity results
    graph_weight=0.3,     # weight of graph-traversal results
    memory_weight=0.2,    # weight of agent memory results
    filters={"category": "infrastructure"},
)

for r in results:
    print(f"[{r['source']}] score={r['score']:.3f}: {r['content'][:80]}")
```

## Data Structures

<AccordionGroup>
  <Accordion title="Decision schema">

```python
@dataclass
class Decision:
    decision_id:    str
    category:       str
    scenario:       str
    reasoning:      str
    outcome:        str
    confidence:     float       # 0.0 – 1.0
    decision_maker: str
    timestamp:      datetime
    entities:       List[str]
    metadata:       Dict
    causal_chain:   List[str]   # IDs of related decisions
```

  </Accordion>
  <Accordion title="Precedent schema">

```python
@dataclass
class Precedent:
    decision_id:    str
    similarity:     float        # 0–1 match score to current scenario
    category:       str
    scenario:       str
    outcome:        str
    reasoning:      str
    confidence:     float
    timestamp:      datetime
```

  </Accordion>
  <Accordion title="PolicyException schema">

```python
@dataclass
class PolicyException:
    exception_id:   str
    policy_rule:    str          # name of the rule that was violated
    decision_id:    str          # the decision that triggered the exception
    justification:  str          # why the exception was granted
    approved_by:    str          # approver identity
    timestamp:      datetime
    expiry:         Optional[datetime]
```

  </Accordion>
  <Accordion title="ApprovalChain schema">

```python
@dataclass
class ApprovalChain:
    chain_id:       str
    decision_id:    str
    steps:          List[ApprovalStep]
    status:         str          # "pending" | "approved" | "rejected"
    created_at:     datetime

@dataclass
class ApprovalStep:
    step_id:        str
    approver:       str
    required:       bool
    status:         str          # "pending" | "approved" | "rejected"
    comment:        Optional[str]
    timestamp:      Optional[datetime]
```

  </Accordion>
  <Accordion title="LinkedEntity schema">

```python
@dataclass
class LinkedEntity:
    text:           str
    canonical_form: str          # normalized primary name
    uri:            str          # e.g. "http://dbpedia.org/resource/Apple_Inc."
    confidence:     float
    sources:        List[str]    # source documents that mention this entity
    aliases:        List[str]    # all observed surface forms
```

  </Accordion>
</AccordionGroup>

## Real-World Patterns

<Tabs>
  <Tab title="Healthcare — Treatment Decisions">
    ```python
    from semantica.context import AgentContext
    from semantica.vector_store import VectorStore

    health_agent = AgentContext(
        vector_store=VectorStore(backend="faiss", dimension=768),
        decision_tracking=True,
    )

    health_agent.store("Patient has hypertension, type 2 diabetes")
    health_agent.store("Patient allergic to penicillin — verified 2024-01")

    decision_id = health_agent.record_decision(
        category="treatment_plan",
        scenario="Hypertension with comorbid diabetes",
        reasoning="ACE inhibitors are renoprotective in diabetic patients — preferred over beta blockers",
        outcome="prescribed_lisinopril",
        confidence=0.91,
    )

    precedents = health_agent.find_precedents("hypertension diabetes", limit=5)
    for p in precedents:
        print(f"Past decision: {p.outcome}  (similarity: {p.similarity:.2f})")
    ```
  </Tab>
  <Tab title="Finance — Loan Decisions">
    ```python
    from semantica.context import AgentContext
    from semantica.vector_store import VectorStore

    loan_agent = AgentContext(
        vector_store=VectorStore(backend="faiss", dimension=768),
        decision_tracking=True,
    )

    loan_agent.store("Applicant: credit score 750, DTI 28%, stable employment 4yr")

    decision_id = loan_agent.record_decision(
        category="loan_approval",
        scenario="First-time homebuyer — 30yr fixed, 20% down",
        reasoning="Credit score above threshold, DTI within limits, stable income verified",
        outcome="approved_300k",
        confidence=0.94,
    )
    ```
  </Tab>
</Tabs>

## Tips and Common Pitfalls

<Warning>
  **Persist your vector store between runs.** Use `VectorStore(backend="faiss", index_path="context.faiss")` — without a path, the FAISS index lives in memory and is lost on shutdown. An agent that forgets everything on restart isn't an agent.
</Warning>

<Warning>
  **Enable `decision_tracking=True` from the start.** Adding it retroactively means historical decisions aren't linked to the causal chain — you lose the ability to trace how one decision influenced later ones. Enable it at agent initialization, even if you're not using it immediately.
</Warning>

<Tip>
  **Use `find_precedents()` before every significant decision.** This is how the context module prevents agents from making contradictory choices across runs. If precedents exist, surface them to the LLM as context — "we chose X for similar reasons before."
</Tip>

<Tip>
  **Set `ttl_days` to avoid memory bloat.** Without TTL, `AgentMemory` accumulates indefinitely. For operational agents, 30–90 day TTL keeps memory relevant to current context. Compliance-critical agents may need `ttl_days=None` (keep forever) with explicit archival.
</Tip>

<Warning>
  **Use `PolicyEngine` before recording irreversible decisions.** Decisions recorded with `record_decision()` become part of the causal chain immediately. If you need a human approval gate, validate first with `policy.validate()` and create an `ApprovalChain` — don't record until approved.
</Warning>

<Tip>
  **`ContextRetriever` is richer than direct vector search.** The three-channel fusion (vector + graph + memory) surfaces results that pure vector search misses — especially for decisions with complex causal relationships. Use it when you need comprehensive context assembly, not just semantic similarity.
</Tip>

<Tip>
  **`EntityLinker` prevents entity proliferation.** Without it, "Apple", "Apple Inc.", and "AAPL" land as three separate nodes in `ContextGraph`. Run `EntityLinker` on mentions before storing them to maintain a clean, canonical graph.
</Tip>

<CardGroup cols={2}>
  <Card title="Vector Store" icon="database" href="vector_store">
    Embedding storage backend for memory retrieval.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Graph algorithms and analytics used inside ContextGraph.
  </Card>
  <Card title="Reasoning" icon="microchip" href="reasoning">
    Logical inference layered on top of context.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    W3C PROV-O lineage for every stored fact.
  </Card>
</CardGroup>

### Cookbooks

- [Context Module](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/19_Context_Module.ipynb) — memory and decision tracking · Intermediate
- [Advanced Context Engineering](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/11_Advanced_Context_Engineering.ipynb) — production FAISS + Neo4j setup · Advanced
- [Decision Tracking with KG Algorithms](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/12_Decision_Tracking_KG.ipynb) — precedent search, policy enforcement · Advanced
