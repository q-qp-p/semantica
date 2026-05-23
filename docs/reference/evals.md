---
title: "Evals Module"
description: "Evaluation framework for measuring Knowledge Graph quality, extraction accuracy, and pipeline performance."
icon: "chart-line"
---

`semantica.evals` provides a comprehensive evaluation framework for measuring extraction accuracy, graph quality, and pipeline performance. Use it to benchmark extractors, validate pipeline output, and track quality regressions across runs.

## What You Get

<CardGroup cols={2}>
  <Card title="KGEvaluator" icon="diagram-project">
    Completeness, consistency, schema compliance, coverage, and orphan node metrics.
  </Card>
  <Card title="ExtractionEvaluator" icon="magnifying-glass">
    NER precision / recall / F1 and relation extraction metrics against gold-standard datasets.
  </Card>
  <Card title="PipelineEvaluator" icon="gear">
    Throughput (docs/sec), per-step latency, peak memory, and error rate benchmarking.
  </Card>
  <Card title="RegressionTracker" icon="clock-rotate-left">
    Record pipeline runs and compare metrics across commits or config changes.
  </Card>
  <Card title="Deduplication Accuracy" icon="copy">
    Merge precision, false positive / false negative rates for deduplication strategies.
  </Card>
  <Card title="Reasoning Correctness" icon="microchip">
    Inference accuracy, rule coverage, and derivation depth for reasoning engines.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Evaluate KG quality">
    ```python
    from semantica.evals import KGEvaluator

    evaluator = KGEvaluator()
    report    = evaluator.evaluate(kg, ontology=ontology)

    print(f"Completeness: {report.completeness:.2%}")
    print(f"Consistency:  {report.consistency:.2%}")
    print(f"Coverage:     {report.coverage:.2%}")
    print(f"Orphan nodes: {report.orphan_count}")
    ```
  </Step>
  <Step title="Evaluate extraction accuracy against gold standard">
    ```python
    from semantica.evals import ExtractionEvaluator

    evaluator = ExtractionEvaluator()
    report    = evaluator.evaluate_ner(
        predictions=extracted_entities,
        gold_standard=annotated_entities,
    )

    print(f"Precision: {report.precision:.3f}")
    print(f"Recall:    {report.recall:.3f}")
    print(f"F1:        {report.f1:.3f}")
    print(f"By type:   {report.per_type_metrics}")
    ```
  </Step>
  <Step title="Benchmark pipeline throughput">
    ```python
    from semantica.evals import PipelineEvaluator

    evaluator = PipelineEvaluator()
    metrics   = evaluator.benchmark(pipeline, data="data/", warmup_runs=2, bench_runs=5)

    print(f"Throughput:       {metrics.docs_per_second:.1f} docs/sec")
    print(f"Total duration:   {metrics.total_seconds:.1f}s")
    print(f"Per-step latency: {metrics.step_latencies}")
    print(f"Peak memory (MB): {metrics.peak_memory_mb:.0f}")
    print(f"Error rate:       {metrics.error_rate:.2%}")
    ```
  </Step>
  <Step title="Track regressions across releases">
    ```python
    from semantica.evals import RegressionTracker

    tracker = RegressionTracker(db_path="eval_history.db")

    run_id = tracker.record_run(
        pipeline_version="v1.2.0",
        metrics=metrics,
        config=config.to_dict(),
    )

    diff = tracker.compare(run_id, baseline_run_id="run_abc123")
    for metric, change in diff.items():
        direction = "↑" if change > 0 else "↓"
        print(f"  {metric}: {direction} {abs(change):.2%}")
    ```
  </Step>
</Steps>

## Evaluation Areas

<Tabs>
  <Tab title="KG Quality">
    Measure completeness, consistency, schema compliance, and structural health of a knowledge graph:

    ```python
    from semantica.evals import KGEvaluator

    evaluator = KGEvaluator()
    report    = evaluator.evaluate(kg, ontology=ontology)

    print(f"Completeness:  {report.completeness:.2%}")   # % entities with all required fields
    print(f"Consistency:   {report.consistency:.2%}")    # % entities without type conflicts
    print(f"Coverage:      {report.coverage:.2%}")       # % entity types in ontology
    print(f"Total nodes:   {report.node_count}")
    print(f"Orphan nodes:  {report.orphan_count}")       # nodes with no edges
    ```

    **Key behaviours:**
    - `consistency` requires an ontology — without one, it always returns 1.0
    - `orphan_count` flags disconnected nodes that likely represent extraction or deduplication errors
    - `completeness` checks required properties defined in the ontology schema
  </Tab>
  <Tab title="Extraction Accuracy">
    Compare extracted entities and relations against annotated gold-standard data:

    ```python
    from semantica.evals import ExtractionEvaluator

    evaluator = ExtractionEvaluator()

    # NER evaluation
    ner_report = evaluator.evaluate_ner(
        predictions=extracted_entities,
        gold_standard=annotated_entities,
    )
    print(f"Precision:    {ner_report.precision:.3f}")
    print(f"Recall:       {ner_report.recall:.3f}")
    print(f"F1:           {ner_report.f1:.3f}")
    print(f"By type:      {ner_report.per_type_metrics}")

    # Relation extraction evaluation
    rel_report = evaluator.evaluate_relations(
        predictions=extracted_relations,
        gold_standard=annotated_relations,
    )
    print(f"Relation F1:  {rel_report.f1:.3f}")
    ```
  </Tab>
  <Tab title="Pipeline Performance">
    Benchmark throughput, latency, memory, and error rate across multiple runs:

    ```python
    from semantica.evals import PipelineEvaluator

    evaluator = PipelineEvaluator()
    metrics   = evaluator.benchmark(
        pipeline,
        data="data/",
        warmup_runs=2,    # eliminate cold-start noise
        bench_runs=5,     # average over 5 real runs
    )

    print(f"Throughput:       {metrics.docs_per_second:.1f} docs/sec")
    print(f"Total duration:   {metrics.total_seconds:.1f}s")
    print(f"Per-step latency: {metrics.step_latencies}")
    print(f"Peak memory (MB): {metrics.peak_memory_mb:.0f}")
    print(f"Error rate:       {metrics.error_rate:.2%}")
    ```
  </Tab>
  <Tab title="Regression Tracking">
    Store runs and compare metrics across pipeline versions:

    ```python
    from semantica.evals import RegressionTracker

    tracker = RegressionTracker(db_path="eval_history.db")

    # Record a run with version tag and full config snapshot
    run_id = tracker.record_run(
        pipeline_version="v1.2.0",
        metrics=metrics,
        config=config.to_dict(),
    )

    # Compare to a previous run
    diff = tracker.compare(run_id, baseline_run_id="run_abc123")
    for metric, change in diff.items():
        direction = "↑" if change > 0 else "↓"
        print(f"  {metric}: {direction} {abs(change):.2%}")
    ```
  </Tab>
</Tabs>

## When to Evaluate

| Trigger | Evaluator to Use | What to Check |
| ------- | ---------------- | ------------- |
| New extraction model or method | `ExtractionEvaluator` | Precision, recall, F1 vs gold standard |
| After changing LLM provider | `ExtractionEvaluator` | Per-type F1 — check if rare types regressed |
| Before releasing new pipeline version | `PipelineEvaluator` | Throughput, latency, error rate |
| After deduplication strategy change | `KGEvaluator` | Orphan count, consistency score |
| Every production deployment | `RegressionTracker` | Compare vs previous baseline run |

## Tips and Common Pitfalls

<Warning>
  **Build a gold standard dataset early.** `ExtractionEvaluator` requires annotated ground truth. Without it, you're evaluating subjectively. Even 100 carefully annotated documents give you a meaningful baseline to track regressions against.
</Warning>

<Tip>
  **Evaluate per entity type, not just overall F1.** Aggregate F1 can hide regressions — if your model's PERSON F1 drops from 0.95 to 0.80 but ORGANIZATION improves, the average may look stable. Use `report.per_type_metrics` to catch type-specific regressions.
</Tip>

<Tip>
  **Store every benchmark run with `RegressionTracker`.** Run ID + version tag + config snapshot gives you a reproducible audit trail. Without it, "did the last release make things better?" has no objective answer.
</Tip>

<Tip>
  **Run `PipelineEvaluator` with `warmup_runs=2`.** Cold starts are unrepresentative — model weights get cached, JIT compilation kicks in. Warmup runs eliminate this noise from your benchmark numbers.
</Tip>

<Warning>
  **`KGEvaluator` needs an ontology for consistency scoring.** Without an ontology, `consistency` always returns 1.0 — there's nothing to check against. Pass `ontology=ontology` to get meaningful consistency metrics.
</Warning>

<CardGroup cols={2}>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extraction module to evaluate.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Graph quality assessment.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Pipeline performance metrics.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Deduplication accuracy evaluation.
  </Card>
</CardGroup>
