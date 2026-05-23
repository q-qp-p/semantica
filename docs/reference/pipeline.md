---
title: "Pipeline Module"
description: "Pipeline DSL with parallel workers, retry policies, failure handling, and progress tracking."
icon: "gear"
---

`semantica.pipeline` lets you chain Semantica components into reproducible, fault-tolerant workflows with parallel execution and configurable error handling. Pipelines are serializable — save them to YAML and reload in any environment.

## Why Use a Pipeline?

You could wire Semantica modules together with plain Python code. Pipelines add:

<CardGroup cols={2}>
  <Card title="Retry and failure handling" icon="arrow-rotate-right">
    A single bad document doesn't crash a 10,000-document run.
  </Card>
  <Card title="Parallelism" icon="bolt">
    Run extraction across multiple workers with one parameter.
  </Card>
  <Card title="Progress tracking" icon="chart-line">
    tqdm console bar or WebSocket streaming to Explorer.
  </Card>
  <Card title="Reproducibility" icon="floppy-disk">
    Save the exact pipeline configuration to YAML and replay on any machine.
  </Card>
  <Card title="Delta mode" icon="code-compare">
    On re-runs, only process documents that changed since the last run.
  </Card>
  <Card title="Validation" icon="shield-check">
    Catch misconfigured steps and dependency cycles before they fail mid-run.
  </Card>
</CardGroup>

<Note>
  Use plain module calls for quick scripts and notebooks. Use pipelines for anything you run repeatedly, at scale, or in production.
</Note>

<img src="/assets/img/diagrams/pipeline-flow.svg" alt="Pipeline step sequence: Ingest → Parse → Normalize → Extract → Build KG → QA → Store → Deliver" style={{ width: '100%', borderRadius: '10px', margin: '0 0 24px' }} />

## Quick Start

<Steps>
  <Step title="Create a pipeline and add steps">
    ```python
    from semantica.pipeline import Pipeline
    from semantica.ingest import FileIngestor
    from semantica.parse import DocumentParser
    from semantica.semantic_extract import NERExtractor
    from semantica.kg import GraphBuilder
    from semantica.llms import Groq
    import os

    llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

    pipeline = Pipeline()
    pipeline.add_step("ingest",   FileIngestor())
    pipeline.add_step("parse",    DocumentParser())
    pipeline.add_step("extract",  NERExtractor(method="llm", llm_provider=llm))
    pipeline.add_step("build_kg", GraphBuilder(merge_entities=True))
    ```
  </Step>
  <Step title="Validate before running">
    ```python
    from semantica.pipeline import PipelineValidator

    validator = PipelineValidator()
    result = validator.validate_pipeline(pipeline)

    if not result.is_valid:
        for error in result.errors:
            print(f"Error: {error.message}  (step: {error.step})")
    ```
  </Step>
  <Step title="Run and inspect results">
    ```python
    result = pipeline.run("data/", show_progress=True)

    kg = result.output
    print(f"Processed: {result.processed_count}")
    print(f"Failed:    {result.failed_count}")
    print(f"Duration:  {result.duration_seconds:.1f}s")
    ```
  </Step>
</Steps>

## Parallel Processing

Process documents concurrently across multiple workers:

```python
pipeline = Pipeline(workers=4)

pipeline.add_step("ingest",  FileIngestor())
pipeline.add_step("parse",   DocumentParser())
pipeline.add_step("extract", NERExtractor(), parallel=True, batch_size=10)
pipeline.add_step("build",   GraphBuilder())

result = pipeline.run("data/")
```

## Retry and Error Handling

<Tabs>
  <Tab title="Exponential backoff (recommended)">
    ```python
    from semantica.pipeline import RetryPolicy, FailureHandler, Pipeline

    retry = RetryPolicy(
        max_retries=3,
        backoff="exponential",
        initial_delay=1.0    # 1s → 2s → 4s
    )

    handler = FailureHandler(strategy="skip", log_failures=True)

    pipeline = Pipeline(retry_policy=retry, failure_handler=handler)
    ```

    Best for transient API errors and rate limits — waits longer with each retry, giving upstream services time to recover.
  </Tab>
  <Tab title="Linear backoff">
    ```python
    retry = RetryPolicy(
        max_retries=3,
        backoff="linear",
        initial_delay=2.0    # 2s → 4s → 6s
    )
    ```

    Use when the delay between retries should grow predictably — e.g., waiting for a database lock to release.
  </Tab>
  <Tab title="Fixed backoff">
    ```python
    retry = RetryPolicy(
        max_retries=5,
        backoff="fixed",
        initial_delay=1.0    # 1s → 1s → 1s → 1s → 1s
    )
    ```

    Use when retrying against a service with a fixed cooldown window.
  </Tab>
</Tabs>

### Failure Strategies

| Strategy | Behaviour | When to Use |
| -------- | --------- | ----------- |
| `"skip"` | Log failure, continue to next document | Production — one bad doc shouldn't stop 10k |
| `"stop"` | Raise exception immediately | Development — surface errors fast |
| `"retry"` | Retry via `RetryPolicy`, then skip | When failures are likely transient |

<Warning>
  Always use `strategy="skip"` in production. A single malformed document shouldn't stop a pipeline processing thousands of documents. Inspect `result.errors` after the run to find and reprocess failures.
</Warning>

## Progress Tracking

<Tabs>
  <Tab title="Console (tqdm)">
    ```python
    result = pipeline.run("data/", show_progress=True)
    ```

    Displays a live tqdm progress bar in the terminal. Best for scripts and CLI tools.
  </Tab>
  <Tab title="WebSocket (Explorer)">
    ```python
    result = pipeline.run("data/", websocket_port=8080)
    ```

    Streams progress events to Knowledge Explorer's dashboard. Best for long-running production jobs where you want a live web UI.
  </Tab>
</Tabs>

## Pipeline DSL

`PipelineBuilder` provides a fluent chain syntax that reads as a data flow:

```python
from semantica.pipeline import PipelineBuilder

pipeline = (
    PipelineBuilder()
    .ingest(FileIngestor())
    .parse(DocumentParser())
    .normalize()
    .extract(NERExtractor(method="llm", llm_provider=llm))
    .extract_relations(RelationExtractor(method="llm", llm_provider=llm))
    .build_kg(merge_entities=True)
    .deduplicate(strategy="semantic_v2")
    .export(format="turtle", path="output.ttl")
    .build()
)

result = pipeline.run("data/")
```

## Save and Load Pipelines

Serialize a pipeline to YAML for reproducible runs across environments:

```python
# Save pipeline configuration
pipeline.save("pipeline_config.yaml")

# Load and run on any machine
pipeline = Pipeline.load("pipeline_config.yaml")
result = pipeline.run("data/")
```

<Tip>
  `pipeline.save()` preserves exact component configurations — LLM model names, retry policies, thresholds — everything. Without it, you can't guarantee that a re-run 3 months later uses the same settings.
</Tip>

## Pre-Built Templates

`PipelineTemplateManager` wires common workflows with the correct step order — no manual wiring required:

```python
from semantica.pipeline import PipelineTemplateManager
from semantica.llms import Groq
import os

llm     = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
manager = PipelineTemplateManager()
```

<CardGroup cols={2}>
  <Card title="ingest-extract-build" icon="diagram-project">
    **Ingest → Parse → Extract → Build KG**

    Standard knowledge base construction from documents.

    ```python
    pipeline = manager.get_template(
        "ingest-extract-build", llm_provider=llm
    )
    ```
  </Card>
  <Card title="graphrag" icon="magnifying-glass">
    **Ingest → Parse → Embed → Index**

    Retrieval-augmented generation — builds a vector-indexed knowledge graph.

    ```python
    pipeline = manager.get_template(
        "graphrag", llm_provider=llm, vector_backend="faiss"
    )
    ```
  </Card>
  <Card title="analytics" icon="chart-bar">
    **Build KG → Analytics → Export Report**

    Graph analysis and reporting — centrality, community detection, HTML output.

    ```python
    pipeline = manager.get_template(
        "analytics", export_format="html"
    )
    ```
  </Card>
  <Card title="full-qa" icon="shield-check">
    **Ingest → Normalize → Extract → Dedup → Conflicts → Build**

    Production-quality KG with full data quality pipeline.

    ```python
    pipeline = manager.get_template(
        "full-qa", llm_provider=llm
    )
    ```
  </Card>
</CardGroup>

## ExecutionEngine

Fine-grained control over pipeline execution — pause, resume, cancel, and inspect live progress:

```python
from semantica.pipeline import ExecutionEngine

engine = ExecutionEngine(config={"timeout_seconds": 300, "max_workers": 4})

result = engine.execute_pipeline(pipeline, data="data/")

# Pause after the current step finishes
engine.pause_pipeline(result.pipeline_id)

progress = engine.get_progress(result.pipeline_id)
print(f"Completed: {progress['completed']}/{progress['total']}")
print(f"Current step: {progress['current_step']}")

engine.resume_pipeline(result.pipeline_id)
engine.stop_pipeline(result.pipeline_id)
```

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `execute_pipeline(pipeline, data)` | `ExecutionResult` | Execute pipeline from start to finish |
| `get_status(pipeline_id)` | `PipelineStatus` | Current state (RUNNING, PAUSED, STOPPED) |
| `get_progress(pipeline_id)` | `Dict` | Step completion counts and elapsed time |
| `pause_pipeline(pipeline_id)` | `None` | Suspend after current step completes |
| `resume_pipeline(pipeline_id)` | `None` | Resume from paused state |
| `stop_pipeline(pipeline_id)` | `None` | Cancel and clean up immediately |

## PipelineValidator

Catches problems before they surface as mid-run failures:

```python
from semantica.pipeline import PipelineValidator

validator = PipelineValidator()
result    = validator.validate_pipeline(pipeline)

if result.is_valid:
    print("Pipeline is valid — safe to run")
else:
    for error in result.errors:
        print(f"Error: {error.message}  (step: {error.step})")
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

Checks performed:
- **Dependency cycle detection** — A depends on B, B depends on A
- **Step type validation** — each step type must be registered
- **Connection integrity** — referenced step names must exist
- **Configuration completeness** — required parameters must be present

## ParallelismManager

<Tabs>
  <Tab title="Thread pool (I/O-bound)">
    ```python
    from semantica.pipeline import ParallelismManager

    manager = ParallelismManager(max_workers=8, pool_type="thread")

    tasks  = [{"fn": ner.extract, "args": [text]} for text in texts]
    result = manager.execute_parallel(tasks, timeout=60)

    print(f"Successful: {result.success_count}, Failed: {result.failure_count}")
    ```

    Use thread pools for **I/O-bound** steps: web fetching, database queries, API calls. Threads share memory and context-switch cheaply between waiting operations.
  </Tab>
  <Tab title="Process pool (CPU-bound)">
    ```python
    manager = ParallelismManager(max_workers=4, pool_type="process")

    tasks  = [{"fn": embedder.embed, "args": [chunk]} for chunk in chunks]
    result = manager.execute_parallel(tasks, timeout=120)
    ```

    Use process pools for **CPU-bound** steps: embedding computation, OCR, large NER batches. Processes bypass Python's GIL for true multi-core parallelism.
  </Tab>
</Tabs>

## ResourceScheduler

Prevents memory oversubscription on large runs:

```python
from semantica.pipeline import ResourceScheduler

scheduler = ResourceScheduler()

resources = scheduler.allocate_resources(
    pipeline, max_memory_gb=8, max_workers=4
)

try:
    result = pipeline.run("data/")
finally:
    scheduler.release_resources(resources)
```

## Delta Mode

Re-process only data that has changed since the last run:

```python
pipeline = Pipeline()
pipeline.add_step(
    "ingest",  FileIngestor(),
    delta_mode=True, base_version_id="v1", target_version_id="v2"
)
pipeline.add_step(
    "extract", NERExtractor(),
    delta_mode=True, base_version_id="v1", target_version_id="v2"
)
pipeline.add_step(
    "build", GraphBuilder(),
    delta_mode=False  # always rebuild the merged graph
)

result = pipeline.run("data/")
print(f"Delta documents processed: {result.metadata.get('delta_count', 0)}")
print(f"Skipped (unchanged):       {result.metadata.get('skipped_count', 0)}")
```

<Note>
  Delta detection uses SHA-256 checksums on source content. Only sources whose checksum differs from `base_version_id` are passed to downstream steps. For pipelines that run hourly or daily against a growing corpus, delta mode eliminates redundant re-embedding and re-extraction.
</Note>

## Schemas

<AccordionGroup>
  <Accordion title="PipelineResult schema">

```python
@dataclass
class PipelineResult:
    output:           Any      # final step output (e.g., a KnowledgeGraph)
    processed_count:  int      # documents successfully processed
    failed_count:     int      # documents that failed after retries
    duration_seconds: float    # total wall-clock time
    step_metrics:     Dict     # per-step timing and counts
    errors:           List     # list of FailedDocument records
    metadata:         Dict     # pipeline-level metadata (delta_count, etc.)
```

  </Accordion>
  <Accordion title="PipelineStep schema">

```python
@dataclass
class PipelineStep:
    name:              str
    step_type:         str
    config:            Dict[str, Any]
    dependencies:      List[str]          # names of steps this step waits for
    handler:           Optional[Callable]
    status:            StepStatus
    result:            Any
    error:             Optional[Exception]
    delta_mode:        bool               # True = process only changed data
    base_version_id:   Optional[str]     # snapshot ID to diff against
    target_version_id: Optional[str]     # snapshot ID being produced
```

  </Accordion>
  <Accordion title="StepStatus enum">

```python
from semantica.pipeline import StepStatus

StepStatus.PENDING    # Not yet started
StepStatus.RUNNING    # Currently executing
StepStatus.COMPLETED  # Finished successfully
StepStatus.FAILED     # Error occurred — check step.error
StepStatus.SKIPPED    # Skipped due to FailureHandler "skip" strategy
```

  </Accordion>
</AccordionGroup>

## Tips and Common Pitfalls

<Tip>
  **Use `PipelineValidator` before running in production.** It catches dependency cycles, missing step names, and misconfigured connections that would only surface as errors mid-run. Validation is instant; catching them after a 30-minute extraction job is not.
</Tip>

<Tip>
  **Set `workers=` based on workload type.** Thread workers for I/O-bound steps (web fetching, DB queries), process workers for CPU-bound steps (embedding, OCR, large NER batches). Mixing pool types on the wrong step type wastes resources without speed gains.
</Tip>

<Warning>
  **Use `failure_handler=FailureHandler(strategy="skip")` in production.** A single malformed document shouldn't stop a pipeline processing 10,000 documents. `skip` logs the failure and continues; inspect `result.errors` after the run to find and reprocess failed documents.
</Warning>

<Tip>
  **Use templates from `PipelineTemplateManager` for common patterns.** `get_template("full-qa")` wires up normalization, deduplication, conflict detection, and graph construction in the right order — saving you from common mistakes like deduplicating before normalizing.
</Tip>

<Tip>
  **Inspect `result.step_metrics` to find bottlenecks.** Each step reports its own duration and document count. If embedding is 10x slower than NER, that's where to optimize — increase `batch_size`, switch to a faster embedding model, or parallelize with GPU.
</Tip>

<CardGroup cols={2}>
  <Card title="Ingest" icon="database" href="ingest">
    First step in most pipelines.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Core extraction step.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Graph construction step.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Final output step.
  </Card>
</CardGroup>
