---
title: "Reasoning Module"
description: "Forward chaining, Rete, deductive, abductive, SPARQL, Datalog, and temporal reasoning with explainable inference paths."
icon: "microchip"
---

`semantica.reasoning` derives new knowledge from existing facts using logical rules. Every engine produces **explainable inference paths** — traceable chains of rules and facts, not black-box conclusions.

## Why Reasoning?

Knowledge graphs encode what you know explicitly. Reasoning lets you derive what must logically follow — without manually asserting every implication:

- If A `located_in` B and B `located_in` C, then A `located_in` C — without storing that triple
- If Alice `parent_of` Bob and Bob `parent_of` Charlie, then Alice `ancestor_of` Charlie
- If a drug is contraindicated for a condition class, it's also contraindicated for all subclasses — inferred from the ontology hierarchy
- If an employee's CEO tenure ended in 2020, they cannot have signed contracts as CEO in 2021 — caught by temporal reasoning

Reasoning turns sparse explicit knowledge into a dense, coherent, contradiction-free knowledge base.

## What You Get

<CardGroup cols={2}>
  <Card title="Reasoner" icon="bolt">
    Main facade — IF/THEN forward-chaining with variable substitution and rule templates.
  </Card>
  <Card title="GraphReasoner" icon="diagram-project">
    Inference over full knowledge graph structure: transitivity, symmetry, inverses.
  </Card>
  <Card title="ReteEngine" icon="gauge-high">
    High-performance pattern matching via the Rete algorithm for large rule sets.
  </Card>
  <Card title="SPARQLReasoner" icon="table">
    Query expansion and property chain inference over RDF graphs.
  </Card>
  <Card title="DatalogReasoner" icon="rotate">
    Recursive Horn clause rules with guaranteed fixpoint termination (v0.4.0).
  </Card>
  <Card title="TemporalReasoningEngine" icon="clock">
    All 13 Allen interval algebra relations for time-aware inference.
  </Card>
</CardGroup>

<img src="/assets/img/diagrams/reasoning-chain.svg" alt="Forward chaining inference: known facts + IF/THEN rules produce derived facts with a full traceable explanation path" style={{ width: '100%', borderRadius: '12px', margin: '0 0 24px' }} />

## Choosing a Reasoning Engine

| Engine | When to Use |
| ------ | ----------- |
| `Reasoner` | Simple IF/THEN rules, transitivity/symmetry templates, one-shot inference |
| `GraphReasoner` | Rules that operate on graph structure (paths, neighborhoods, multi-hop) |
| `ReteEngine` | Large rule sets (100+), rules fire repeatedly, performance is critical |
| `SPARQLReasoner` | Already using RDF/Turtle, need property chains, SPARQL ecosystem tools |
| `DatalogReasoner` | Recursive rules (ancestry, reachability), guaranteed termination required |
| `TemporalReasoningEngine` | Time-aware facts, interval relationships, historical validity |

## Engines

<Tabs>
  <Tab title="Reasoner">
    The unified entry point for rule-based forward-chaining inference. Start here for most use cases.

    ```python
    from semantica.reasoning import Reasoner, Rule, Fact, RuleType

    reasoner = Reasoner()

    # Add base facts
    reasoner.add_fact(Fact(subject="John", predicate="is_a", obj="Manager"))
    reasoner.add_fact(Fact(subject="John", predicate="is_a", obj="Employee"))

    # Add an IF/THEN rule
    reasoner.add_rule(Rule(
        rule_type=RuleType.FORWARD_CHAIN,
        conditions=[
            {"subject": "?x", "predicate": "is_a", "object": "Manager"}
        ],
        conclusion={"subject": "?x", "predicate": "has_authority", "object": "true"}
    ))

    # Run inference — always call explicitly after adding facts/rules
    result = reasoner.forward_chain()
    for inference in result.derived_facts:
        print(f"{inference.subject} {inference.predicate} {inference.obj}")
        print(f"  Derived via: {inference.explanation}")
    ```

    <Warning>
      Always call `reasoner.forward_chain()` after adding facts and rules. Adding them updates internal state but does **not** trigger inference automatically.
    </Warning>
  </Tab>

  <Tab title="GraphReasoner">
    Inference over the full knowledge graph structure — rules that operate on graph paths, neighborhoods, and multi-hop connections.

    ```python
    from semantica.reasoning import GraphReasoner

    graph_reasoner = GraphReasoner()

    # Define a transitive ancestor rule
    graph_reasoner.add_rule({
        "if": [
            {"subject": "?a", "predicate": "parent_of", "object": "?b"},
            {"subject": "?b", "predicate": "parent_of", "object": "?c"}
        ],
        "then": {"subject": "?a", "predicate": "ancestor_of", "object": "?c"}
    })

    inferences = graph_reasoner.reason(graph, query="")
    for inf in inferences:
        print(f"{inf['subject']} {inf['predicate']} {inf['object']}")
    ```
  </Tab>

  <Tab title="ReteEngine">
    High-performance pattern matching using the Rete algorithm — far faster than naive forward chaining for large rule sets because it caches partial matches across iterations.

    ```python
    from semantica.reasoning import ReteEngine

    engine = ReteEngine()
    engine.load_rules("rules/domain_rules.json")
    results = engine.run(kg)

    # Inspect the Rete network
    root        = engine.get_root()
    alpha_nodes = engine.get_alpha_nodes()   # single-condition filters
    beta_nodes  = engine.get_beta_nodes()    # join nodes
    ```

    Rule file format (JSON):

    ```json
    {
      "rules": [
        {
          "name": "manager_authority",
          "conditions": [
            { "subject": "?x", "predicate": "role",  "object": "Manager" },
            { "subject": "?x", "predicate": "dept",  "object": "?dept"   }
          ],
          "action": {
            "subject": "?x",
            "predicate": "has_authority_over",
            "object": "?dept"
          },
          "priority": 10
        }
      ]
    }
    ```

    | Field | Type | Description |
    | ----- | ---- | ----------- |
    | `name` | `str` | Unique rule identifier — appears in `ExplanationGenerator` output |
    | `conditions` | `List[Dict]` | Pattern to match — use `?variable` for wildcards |
    | `action` | `Dict` | Fact to derive when all conditions match |
    | `priority` | `int` | Higher priority rules fire first |

    <Tip>
      Use `ReteEngine` when you have more than ~20 rules or when rules can fire repeatedly. `Reasoner` re-evaluates all rules from scratch each cycle; `ReteEngine` caches partial matches and is orders of magnitude faster.
    </Tip>
  </Tab>

  <Tab title="SPARQLReasoner">
    Query-based inference over RDF graphs with property chain support. Use this when you're already in the RDF/Turtle ecosystem.

    ```python
    from semantica.reasoning import SPARQLReasoner

    reasoner = SPARQLReasoner(graph=rdf_graph)

    result = reasoner.query("""
        PREFIX ex: <http://example.org/>
        SELECT ?person ?company WHERE {
            ?person ex:founded ?company .
            ?company ex:located_in ex:SiliconValley .
        }
    """)

    for row in result.bindings:
        print(row["person"], row["company"])

    # Property chain inference: A knows B, B colleague_of C ⟹ A knows C
    reasoner.add_property_chain("knows", ["knows", "colleague_of"])
    inferences = reasoner.infer_property_chains()
    ```
  </Tab>

  <Tab title="DatalogReasoner">
    Pure-Python bottom-up semi-naive fixpoint evaluation for recursive Horn clause rules. Termination is **guaranteed** — the engine detects fixpoint convergence and stops.

    <Note>
      Added in **v0.4.0**. Use `DatalogReasoner` whenever your rules can create cycles — it's the only engine with a termination guarantee.
    </Note>

    ```python
    from semantica.reasoning import DatalogReasoner, DatalogFact, DatalogRule

    datalog = DatalogReasoner()

    # Base facts
    datalog.add_fact(DatalogFact("parent", ("alice", "bob")))
    datalog.add_fact(DatalogFact("parent", ("bob",   "charlie")))

    # Recursive rules (Horn clauses)
    datalog.add_rule(DatalogRule("ancestor(?X, ?Y) :- parent(?X, ?Y)."))
    datalog.add_rule(DatalogRule("ancestor(?X, ?Z) :- parent(?X, ?Y), ancestor(?Y, ?Z)."))

    # Evaluate to fixpoint
    datalog.evaluate()

    # Query
    results = datalog.query("ancestor(alice, ?Z)")
    # → [{"Z": "bob"}, {"Z": "charlie"}]
    ```

    <Warning>
      `Reasoner` has **no cycle detection** — rules that create cycles (A derives B, B derives C, C re-derives A) will loop infinitely. Use `DatalogReasoner` whenever recursive rules are involved.
    </Warning>
  </Tab>

  <Tab title="TemporalReasoningEngine">
    Reason about time intervals using all 13 Allen interval algebra relations.

    ```python
    from semantica.reasoning import TemporalReasoningEngine, TemporalInterval, IntervalRelation

    engine = TemporalReasoningEngine()

    ceo_tenure   = TemporalInterval(start="1997-09-16", end="2011-08-24")
    board_member = TemporalInterval(start="2000-01-01", end="2012-06-01")

    relation = engine.get_relation(ceo_tenure, board_member)
    # → IntervalRelation.DURING  (ceo_tenure is fully inside board_member)
    ```

    All 13 Allen interval algebra relations:

    | Relation | Meaning |
    | -------- | ------- |
    | `BEFORE` | A ends before B starts |
    | `MEETS` | A ends exactly when B starts |
    | `OVERLAPS` | A starts before B, ends inside B |
    | `DURING` | A is fully inside B |
    | `STARTS` | A and B start together, A ends first |
    | `FINISHES` | A and B end together, A starts later |
    | `EQUALS` | Identical intervals |
    | + 6 inverses | `AFTER`, `MET_BY`, `OVERLAPPED_BY`, `CONTAINS`, `STARTED_BY`, `FINISHED_BY` |
  </Tab>
</Tabs>

## ExplanationGenerator

Generate structured step-by-step explanations for any derived conclusion:

```python
from semantica.reasoning import ExplanationGenerator

generator = ExplanationGenerator(reasoner)

explanation = generator.explain(
    conclusion={"subject": "John", "predicate": "has_authority", "object": "true"}
)

print(explanation.conclusion)
print(f"Confidence: {explanation.confidence:.2f}")
print(explanation.justification.summary)

for step in explanation.reasoning_path.steps:
    indent = "  " * step.depth
    print(f"{indent}Step {step.depth}: {step.fact}")
    print(f"{indent}  via rule: '{step.rule_name}'")
    print(f"{indent}  premises: {step.premises}")
```

<Tip>
  Name every rule with a descriptive string. `ExplanationGenerator` includes the rule name in each derivation step — unnamed rules produce useless explanations like "rule_0 fired." Use names like `"manager_authority"` or `"transitive_location"`.
</Tip>

<AccordionGroup>
  <Accordion title="Explanation schema">

```python
@dataclass
class Explanation:
    conclusion:     Dict[str, str]   # the fact being explained
    confidence:     float            # aggregated rule confidence
    reasoning_path: ReasoningPath    # full derivation trace
    justification:  Justification    # plain-language summary
```

  </Accordion>
  <Accordion title="ReasoningPath and ReasoningStep schemas">

```python
@dataclass
class ReasoningPath:
    steps: List[ReasoningStep]       # ordered derivation steps

@dataclass
class ReasoningStep:
    depth:       int                 # 0 = base fact, n = nth inference
    fact:        Dict[str, str]      # the fact derived at this step
    rule_name:   str                 # name of the rule that fired
    premises:    List[Dict]          # facts that triggered this rule
    confidence:  float               # confidence at this step
```

  </Accordion>
  <Accordion title="Justification schema">

```python
@dataclass
class Justification:
    summary:   str         # one-sentence natural language explanation
    evidence:  List[str]   # list of supporting source facts
```

  </Accordion>
</AccordionGroup>

## Combining Multiple Reasoning Engines

Different engines cover different expressivity levels — compose them for richer inference:

<Steps>
  <Step title="Forward-chain structural rules with Reasoner">
    ```python
    from semantica.reasoning import Reasoner, Rule, Fact, RuleType

    engine = Reasoner()
    engine.add_rule(Rule(
        rule_type=RuleType.FORWARD_CHAIN,
        conditions=[
            {"subject": "?x", "predicate": "located_in", "object": "?y"},
            {"subject": "?y", "predicate": "located_in", "object": "?z"}
        ],
        conclusion={"subject": "?x", "predicate": "located_in", "object": "?z"}
    ))
    structural_result = engine.forward_chain()
    ```
  </Step>
  <Step title="Pass derived facts to DatalogReasoner for recursive closure">
    ```python
    from semantica.reasoning import DatalogReasoner, DatalogFact, DatalogRule

    datalog = DatalogReasoner()
    for fact in structural_result.derived_facts:
        datalog.add_fact(DatalogFact(fact.predicate, (fact.subject, fact.obj)))

    datalog.add_rule(DatalogRule("reachable(?X, ?Z) :- located_in(?X, ?Y), reachable(?Y, ?Z)."))
    datalog.evaluate()
    ```
  </Step>
  <Step title="Filter results to a time window with TemporalReasoningEngine">
    ```python
    from semantica.reasoning import TemporalReasoningEngine
    from datetime import datetime

    temporal = TemporalReasoningEngine()
    active_facts = [
        f for f in datalog.query("reachable(?X, ?Z)")
        if temporal.is_active(f, at=datetime(2024, 1, 1))
    ]
    ```
  </Step>
  <Step title="Explain any conclusion with ExplanationGenerator">
    ```python
    from semantica.reasoning import ExplanationGenerator

    generator = ExplanationGenerator(engine)
    explanation = generator.explain(
        {"subject": "london_office", "predicate": "located_in", "object": "UK"}
    )
    print(explanation.summary)
    ```
  </Step>
</Steps>

## Tips and Common Pitfalls

<Warning>
  **Always call `reasoner.forward_chain()` after adding facts and rules.** Adding facts and rules updates internal state but doesn't trigger inference automatically. Inference is a separate, explicit step.
</Warning>

<Tip>
  **Use `ReteEngine` for large rule sets.** If you have more than ~20 rules and rules can fire repeatedly, `Reasoner` re-evaluates all rules from scratch on each cycle. `ReteEngine` caches partial matches and is orders of magnitude faster for complex rule sets.
</Tip>

<Warning>
  **`DatalogReasoner` guarantees termination; `Reasoner` does not.** If your rules can create cycles (A derives B, B derives C, C re-derives A), `DatalogReasoner`'s semi-naive fixpoint evaluation will stop when no new facts are added. `Reasoner` has no cycle detection and may loop infinitely.
</Warning>

<Tip>
  **Name every rule for readable explanations.** `ExplanationGenerator.explain()` includes the rule name in each derivation step. Unnamed or generic rule names produce useless explanations like "rule_0 fired." Use descriptive names: `"manager_authority"`, `"transitive_location"`.
</Tip>

<Tip>
  **Use rule `priority` to control inference order.** When multiple rules could fire on the same facts, higher-priority rules fire first. This matters when a higher-priority rule produces a fact that gates a lower-priority rule's conditions.
</Tip>

<Tip>
  **Combine engines for maximum expressivity.** Forward-chain structural rules with `Reasoner`, then pass derived facts to `DatalogReasoner` for recursive closure, then filter by time with `TemporalReasoningEngine`. Each engine covers a different expressivity class — they compose cleanly.
</Tip>

<CardGroup cols={2}>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The knowledge graph being reasoned over.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Ontology axioms and SHACL constraints for logical reasoning.
  </Card>
  <Card title="Triplet Store" icon="table" href="triplet_store">
    RDF backend for SPARQL-based reasoning.
  </Card>
  <Card title="Context" icon="brain" href="context">
    Reasoning integrated into agent decision intelligence.
  </Card>
</CardGroup>
