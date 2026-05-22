---
title: "Context Module"
description: "Agent context graphs, decision tracking, causal chains, and precedent search."
icon: "brain"
---

> The intelligent brain for AI agents, providing memory, decision tracking, and knowledge organization.

---

## Overview

The **Context Module** gives your AI agents the ability to remember, learn, and make smarter decisions through intelligent memory management and knowledge organization.

<CardGroup cols={2}>
  <Card title="Smart Memory" icon="memory">
    Human-like memory that stores conversations, learns from experience, and retrieves relevant information when needed.
  </Card>
  <Card title="Decision Intelligence" icon="diagram-project">
    Track decisions, learn from past choices, and make consistent, improving decisions over time.
  </Card>
  <Card title="Easy-to-Use API" icon="code">
    Simple methods that make complex features accessible without overwhelming complexity.
  </Card>
  <Card title="Smart Retrieval" icon="magnifying-glass">
    Find relevant information using hybrid search that understands context and relationships.
  </Card>
  <Card title="Knowledge Organization" icon="sitemap">
    Build intelligent knowledge graphs that understand relationships and context.
  </Card>
  <Card title="Production Ready" icon="check-circle">
    Scalable, reliable, and tested for real-world applications.
  </Card>
</CardGroup>

<Tip>
  **Perfect for:** AI agents that need to remember conversations and learn from decisions, chatbots that become smarter with every interaction, and decision systems that need compliance-ready audit trails.
</Tip>

---

## AgentContext

The main interface that makes your agent intelligent. Handles memory, decisions, and knowledge organization automatically.

### Quick Start

```python
from semantica.context import AgentContext
from semantica.vector_store import VectorStore

agent = AgentContext(vector_store=VectorStore(backend="inmemory", dimension=384))

memory_id = agent.store("User asked about Python programming")
results = agent.retrieve("Python tutorials")
```

### Decision Learning

```python
decision_id = agent.record_decision(
    category="content_recommendation",
    scenario="User wants Python tutorial",
    reasoning="User mentioned being a beginner",
    outcome="recommended_basics",
    confidence=0.85
)

similar_decisions = agent.find_precedents("Python tutorial", limit=3)
```

### Full Setup

```python
agent = AgentContext(
    vector_store=vector_store,
    knowledge_graph=ContextGraph(advanced_analytics=True),
    decision_tracking=True,
    graph_expansion=True,
    advanced_analytics=True,
    kg_algorithms=True,
    vector_store_features=True
)

insights = agent.get_context_insights()
```

### Core Methods

| Method | Description |
|--------|-------------|
| `store(content, ...)` | Remember information |
| `retrieve(query, ...)` | Find relevant memories |
| `record_decision(category, scenario, reasoning, outcome, confidence, ...)` | Learn from decisions |
| `find_precedents(scenario, category, ...)` | Find similar past decisions |
| `analyze_decision_influence(decision_id)` | Analyze downstream impact |
| `get_context_insights()` | Get analytics about your agent |

### GraphRAG with Multi-Hop Reasoning

```python
from semantica.llms import Groq
import os

llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

result = agent.query_with_reasoning(
    query="What technologies work well together?",
    llm_provider=llm,
    max_hops=2
)

print(f"Response: {result['response']}")
print(f"Reasoning: {result['reasoning_path']}")
```

---

## ContextGraph

Organizes complex information and relationships into intelligent knowledge networks.

### Building a Knowledge Graph

```python
from semantica.context import ContextGraph

knowledge = ContextGraph(advanced_analytics=True)

knowledge.add_node("Python", "language", properties={"popularity": "high"})
knowledge.add_node("FastAPI", "framework", properties={"language": "Python"})
knowledge.add_edge("Python", "FastAPI", "supports")
```

### Decision Management

```python
decision_id = knowledge.add_decision_simple(
    category="technology_choice",
    scenario="Framework selection for web API",
    reasoning="FastAPI provides better performance for Python APIs",
    outcome="selected_fastapi",
    confidence=0.92,
    entities=["Python", "FastAPI", "web_project"]
)

similar = knowledge.find_precedents_by_scenario(
    scenario="web framework",
    category="technology_choice",
    limit=3
)

impact = knowledge.analyze_decision_impact(decision_id)
```

### Core ContextGraph Methods

| Method | Description |
|--------|-------------|
| `add_node(node_id, node_type, properties)` | Add concepts to remember |
| `add_edge(source, target, relation)` | Connect related concepts |
| `add_decision_simple(category, scenario, reasoning, outcome, confidence, ...)` | Record decisions |
| `find_precedents_by_scenario(scenario, category, ...)` | Find similar past decisions |
| `analyze_decision_impact(decision_id)` | See how decisions affect others |
| `trace_decision_chain(decision_id)` | Trace decision connections |
| `check_decision_rules(decision_data)` | Validate decisions against policy |
| `find_related_nodes(node_id, how_many)` | Discover connections |

---

## Data Structures

```python
@dataclass
class MemoryItem:
    content: str
    timestamp: datetime
    metadata: Dict
    embedding: List[float]
    entities: List[Dict]

@dataclass
class Decision:
    decision_id: str
    category: str
    scenario: str
    reasoning: str
    outcome: str
    confidence: float        # 0–1
    decision_maker: str
    timestamp: datetime
    entities: List[str]
    metadata: Dict
```

---

## Configuration Options

```python
# Minimal: memory only
agent = AgentContext(vector_store=vector_store)

# Recommended: memory + decision learning
agent = AgentContext(
    vector_store=vector_store,
    decision_tracking=True,
    graph_expansion=True
)

# Full: all features
agent = AgentContext(
    vector_store=vector_store,
    knowledge_graph=ContextGraph(advanced_analytics=True),
    decision_tracking=True,
    graph_expansion=True,
    advanced_analytics=True,
    kg_algorithms=True,
    vector_store_features=True
)

# ContextGraph options
graph = ContextGraph(
    advanced_analytics=True,
    centrality_analysis=True,
    community_detection=True,
    node_embeddings=True
)
```

---

## Real-World Examples

### Banking — Loan Decisions

```python
bank_agent = AgentContext(vector_store=bank_vector_store, decision_tracking=True)

bank_agent.store("Customer has credit score 750, stable employment")

loan_decision = bank_agent.record_decision(
    category="loan_approval",
    scenario="First-time homebuyer mortgage",
    reasoning="Good credit score, stable income, 20% down payment",
    outcome="approved",
    confidence=0.94
)

similar_loans = bank_agent.find_precedents("homebuyer", category="loan_approval")
```

### Healthcare — Treatment Decisions

```python
health_agent = AgentContext(vector_store=medical_vector_store, decision_tracking=True)

health_agent.store("Patient has hypertension, type 2 diabetes")
health_agent.store("Patient allergic to penicillin")

treatment_decision = health_agent.record_decision(
    category="treatment_plan",
    scenario="Hypertension with diabetes",
    reasoning="ACE inhibitors safe for diabetic patients",
    outcome="prescribed_ace_inhibitor",
    confidence=0.91
)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Vector Store" icon="database" href="vector_store">
    Long-term vector storage backend.
  </Card>
  <Card title="KG Module" icon="diagram-project" href="kg">
    Knowledge graph algorithms and analytics.
  </Card>
  <Card title="Reasoning" icon="microchip" href="reasoning">
    Logical inference over context.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    W3C PROV-O lineage tracking.
  </Card>
</CardGroup>

### Cookbook

- [Context Module](https://github.com/semantica-agi/semantica/blob/main/cookbook/introduction/19_Context_Module.ipynb) — practical guide to agent memory and decision tracking · Intermediate
- [Advanced Context Engineering](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/11_Advanced_Context_Engineering.ipynb) — production-grade memory system with FAISS and Neo4j · Advanced
- [Decision Tracking with KG Algorithms](https://github.com/semantica-agi/semantica/blob/main/cookbook/advanced/12_Decision_Tracking_KG.ipynb) — decision lifecycle, precedent search, policy compliance · Advanced
