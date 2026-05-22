---
title: "Reasoning Module"
description: "Forward chaining, Rete, deductive, abductive, SPARQL, Datalog, and temporal reasoning with explainable inference paths."
icon: "microchip"
---

> Logical inference engine supporting rule-based, SPARQL, Rete, Datalog, and temporal reasoning — all with explainable paths.

---

## Overview

The **Reasoning Module** derives new knowledge from existing facts using logical rules. Every engine produces **explainable inference paths** — not black-box conclusions.

<CardGroup cols={2}>
  <Card title="Reasoner" icon="brain">
    Main facade — forward chaining with IF/THEN rules and variable substitution.
  </Card>
  <Card title="ReteEngine" icon="bolt">
    High-performance pattern matching for large rule sets via the Rete algorithm.
  </Card>
  <Card title="SPARQLReasoner" icon="database">
    Query expansion and property chain inference over RDF graphs.
  </Card>
  <Card title="DatalogReasoner" icon="code">
    Recursive Horn clause rules with bottom-up fixpoint semantics (v0.4.0).
  </Card>
  <Card title="TemporalReasoningEngine" icon="clock">
    All 13 Allen interval algebra relations for time-aware inference.
  </Card>
  <Card title="ExplanationGenerator" icon="list-check">
    Structured explanation paths — how each conclusion was derived.
  </Card>
</CardGroup>

---

## Reasoner (Main Facade)

The unified entry point for rule-based forward-chaining inference:

```python
from semantica.reasoning import Reasoner, Rule, Fact, RuleType

reasoner = Reasoner()

# Add facts
reasoner.add_fact(Fact(subject="John", predicate="is_a", obj="Manager"))
reasoner.add_fact(Fact(subject="John", predicate="is_a", obj="Employee"))

# Add rules
reasoner.add_rule(Rule(
    rule_type=RuleType.FORWARD_CHAIN,
    conditions=[
        {"subject": "?x", "predicate": "is_a", "object": "Manager"}
    ],
    conclusion={"subject": "?x", "predicate": "has_authority", "object": "true"}
))

# Run inference
result = reasoner.infer()
for inference in result.derived_facts:
    print(f"{inference.subject} {inference.predicate} {inference.obj}")
    print(f"  Derived via: {inference.explanation}")
```

---

## GraphReasoner

Inference over the full knowledge graph structure:

```python
from semantica.reasoning import GraphReasoner

graph_reasoner = GraphReasoner(kg)

# Infer transitive closure
graph_reasoner.add_rule({
    "if": [
        {"subject": "?a", "predicate": "parent_of", "object": "?b"},
        {"subject": "?b", "predicate": "parent_of", "object": "?c"}
    ],
    "then": {"subject": "?a", "predicate": "ancestor_of", "object": "?c"}
})

inferences = graph_reasoner.infer(kg)
for inf in inferences:
    print(f"{inf['subject']} {inf['predicate']} {inf['object']}")
```

---

## ReteEngine

High-performance pattern matching using the Rete algorithm — far faster than naive forward chaining for large rule sets because it caches partial matches:

```python
from semantica.reasoning import ReteEngine, ReteNode, AlphaNode, BetaNode

engine = ReteEngine()
engine.load_rules("rules/domain_rules.json")
results = engine.run(kg)

# Inspect the network
root: ReteNode = engine.get_root()
alpha_nodes = engine.get_alpha_nodes()   # single-condition filters
beta_nodes  = engine.get_beta_nodes()    # join nodes
```

Rule format for Rete:

```json
{
  "rules": [
    {
      "name": "manager_authority",
      "conditions": [
        { "subject": "?x", "predicate": "role", "object": "Manager" }
      ],
      "action": { "subject": "?x", "predicate": "has_authority", "object": "true" }
    }
  ]
}
```

---

## SPARQLReasoner

Query-based inference over RDF graphs:

```python
from semantica.reasoning import SPARQLReasoner, SPARQLQueryResult

reasoner = SPARQLReasoner(graph=rdf_graph)

result: SPARQLQueryResult = reasoner.query("""
    PREFIX ex: <http://example.org/>
    SELECT ?person ?company WHERE {
        ?person ex:founded ?company .
        ?company ex:located_in ex:SiliconValley .
    }
""")

for row in result.bindings:
    print(row["person"], row["company"])
```

Property chain inference:

```python
# Infer: if A knows B and B is colleague_of C, then A knows C
reasoner.add_property_chain("knows", ["knows", "colleague_of"])
inferences = reasoner.infer_property_chains()
```

---

## DatalogReasoner (v0.4.0)

Pure-Python bottom-up semi-naive fixpoint evaluation for recursive Horn clause rules. Termination is guaranteed:

```python
from semantica.reasoning import DatalogReasoner, DatalogFact, DatalogRule

datalog = DatalogReasoner()

# Add base facts
datalog.add_fact(DatalogFact("parent", ("alice", "bob")))
datalog.add_fact(DatalogFact("parent", ("bob",  "charlie")))

# Add recursive rules (Horn clauses)
datalog.add_rule(DatalogRule("ancestor(?X, ?Y) :- parent(?X, ?Y)."))
datalog.add_rule(DatalogRule("ancestor(?X, ?Z) :- parent(?X, ?Y), ancestor(?Y, ?Z)."))

# Evaluate to fixpoint
datalog.evaluate()

# Query
results = datalog.query("ancestor(alice, ?Z)")
# → [{"Z": "bob"}, {"Z": "charlie"}]
```

<Note>
  Datalog termination is guaranteed — the engine detects fixpoint convergence and stops automatically. No infinite loops.
</Note>

---

## TemporalReasoningEngine

Reason about time intervals using all 13 Allen interval algebra relations:

```python
from semantica.reasoning import TemporalReasoningEngine, TemporalInterval, IntervalRelation

engine = TemporalReasoningEngine()

# Define intervals
ceo_tenure = TemporalInterval(start="1997-09-16", end="2011-08-24")
board_member = TemporalInterval(start="2000-01-01", end="2012-06-01")

# Check interval relations (all 13 Allen relations supported)
relation = engine.get_relation(ceo_tenure, board_member)
# → IntervalRelation.DURING  (ceo_tenure is during board_member)

# Named relations
IntervalRelation.BEFORE       # a ends before b starts
IntervalRelation.MEETS        # a ends exactly when b starts
IntervalRelation.OVERLAPS     # a starts before b, ends inside b
IntervalRelation.DURING       # a is fully inside b
IntervalRelation.STARTS       # a and b start together, a ends first
IntervalRelation.FINISHES     # a and b end together, a starts later
IntervalRelation.EQUALS       # identical intervals
# + 6 inverse relations (AFTER, MET_BY, OVERLAPPED_BY, CONTAINS, STARTED_BY, FINISHED_BY)
```

---

## ExplanationGenerator

Generate structured explanations for inferences:

```python
from semantica.reasoning import ExplanationGenerator, Explanation, ReasoningPath

generator = ExplanationGenerator(reasoner)

explanation: Explanation = generator.explain(
    conclusion={"subject": "John", "predicate": "has_authority", "object": "true"}
)

print(explanation.conclusion)
print(explanation.confidence)

for step in explanation.reasoning_path.steps:
    print(f"  Step {step.depth}: {step.fact} via rule '{step.rule_name}'")
```

---

## Built-In Rule Templates

```python
from semantica.reasoning import Reasoner

engine = Reasoner()

# Apply common logical patterns
engine.apply_transitivity("located_in")   # A→B, B→C ⟹ A→C
engine.apply_symmetry("knows")            # A knows B ⟹ B knows A
engine.apply_inverse("parent_of", "child_of")  # A parent_of B ⟹ B child_of A
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The knowledge graph being reasoned over.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Ontology axioms and SHACL constraints.
  </Card>
  <Card title="Triplet Store" icon="table" href="triplet_store">
    RDF backend for SPARQL reasoning.
  </Card>
  <Card title="Context" icon="brain" href="context">
    Reasoning integrated into agent intelligence.
  </Card>
</CardGroup>
