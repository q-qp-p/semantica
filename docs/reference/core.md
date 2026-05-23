---
title: "Core Module"
description: "Framework orchestration, lifecycle management, configuration, and plugin system."
icon: "gear"
---

`semantica.core` is the coordination layer for the framework. For most tasks you should use individual modules directly (`semantica.ingest`, `semantica.kg`, etc.). Reach for Core when you need application-level lifecycle management, centralized configuration, or a plugin registry.

## What You Get

<CardGroup cols={2}>
  <Card title="Semantica" icon="gear">
    Orchestration class for coordinating complex multi-module workflows and full KG construction pipelines.
  </Card>
  <Card title="ConfigManager" icon="sliders">
    Unified config loading, merging, and validation with environment variable overrides.
  </Card>
  <Card title="LifecycleManager" icon="rotate">
    Startup/shutdown hooks with priority ordering and component health monitoring.
  </Card>
  <Card title="PluginRegistry" icon="plug">
    Dynamic plugin discovery, registration, loading, and unloading.
  </Card>
  <Card title="MethodRegistry" icon="list">
    Register and dispatch custom orchestration methods by name.
  </Card>
  <Card title="Config Class" icon="file-code">
    Live configuration state — dot-notation access, update, validate, and serialize.
  </Card>
</CardGroup>

<Tip>
  **Use individual modules directly** for the vast majority of use cases. Use the `Semantica` orchestration class only when you need application-level lifecycle management or a plugin system.
</Tip>

## Quick Start

<Steps>
  <Step title="Load configuration">
    ```python
    from semantica.core import ConfigManager

    manager = ConfigManager()
    config  = manager.load_from_file("config.yaml")

    # Override one key at runtime
    config.set("processing.batch_size", 64)
    ```
  </Step>
  <Step title="Initialize the framework">
    ```python
    from semantica.core import Semantica

    framework = Semantica(config=config)
    framework.initialize()

    status = framework.get_status()
    print(f"State: {status['state']}")   # → "READY"
    ```
  </Step>
  <Step title="Build a knowledge base">
    ```python
    result = framework.build_knowledge_base(
        sources=["doc1.pdf", "doc2.docx"],
        embeddings=True,
        graph=True,
    )
    ```
  </Step>
  <Step title="Shut down gracefully">
    ```python
    # Always shut down in a finally block
    try:
        result = framework.build_knowledge_base(sources)
    finally:
        framework.shutdown(graceful=True)
    ```
  </Step>
</Steps>

## Semantica (Orchestration)

High-level entry point that coordinates the full KG construction pipeline:

```python
from semantica.core import Semantica, ConfigManager

config_manager = ConfigManager()
config         = config_manager.load_from_file("config.yaml")

framework = Semantica(config=config)
framework.initialize()

try:
    result = framework.build_knowledge_base(
        sources=["doc1.pdf", "doc2.docx"],
        embeddings=True,
        graph=True,
    )
    status = framework.get_status()
    print(f"State: {status['state']}")
finally:
    framework.shutdown(graceful=True)
```

| Method | Description |
| ------ | ----------- |
| `initialize()` | Initialize all framework components |
| `build_knowledge_base(sources, **kwargs)` | Orchestrate full KG construction pipeline |
| `run_pipeline(pipeline, data)` | Execute an existing `Pipeline` instance |
| `get_status()` | Return system health and current state |
| `shutdown(graceful=True)` | Graceful shutdown — waits for in-flight operations |

## ConfigManager

Centralized config loading with deep-merge and environment variable overrides:

```python
from semantica.core import ConfigManager

manager = ConfigManager()
config  = manager.load_from_file("config.yaml")

# Merge base config with environment-specific overrides
merged = manager.merge_configs(
    manager.load_from_file("base.yaml"),
    manager.load_from_file("prod.yaml"),
)

# Nested dot-notation access
batch_size = config.get("processing.batch_size", default=16)
config.set("processing.batch_size", 64)
config.update({"quality": {"min_confidence": 0.75}}, merge=True)
config.validate()

config_dict = config.to_dict()
```

### Config Section Reference

| Section | Key Fields | Description |
| ------- | ---------- | ----------- |
| `llm_provider` | `name`, `model`, `api_key`, `base_url` | LLM used for extraction and reasoning |
| `embedding_model` | `provider`, `model`, `dimension`, `device` | Embedding provider and model |
| `vector_store` | `backend`, `dimension`, `index_type` | Vector storage backend |
| `graph_db` | `backend`, `uri`, `user`, `password` | Graph database connection |
| `processing` | `batch_size`, `max_workers`, `chunk_size` | Parallelism and batching |
| `pipeline` | `retry_max`, `backoff`, `failure_strategy` | Pipeline retry and failure policy |
| `logging` | `level`, `format`, `file` | Logging configuration |
| `quality` | `min_confidence`, `dedup_threshold` | Quality thresholds |
| `security` | `redact_pii`, `allowed_domains` | Security and compliance settings |
| `custom` | any key | User-defined extension settings |

### Environment Variable Overrides

Any config key can be overridden with a `SEMANTICA_` prefix using double underscores for nesting:

```bash
export SEMANTICA_PROCESSING__BATCH_SIZE=64
export SEMANTICA_LLM_PROVIDER__MODEL=gpt-4o
export SEMANTICA_LOGGING__LEVEL=DEBUG
export SEMANTICA_QUALITY__MIN_CONFIDENCE=0.8
```

## LifecycleManager

Manages framework state with a defined state machine and ordered startup/shutdown hooks:

```python
from semantica.core import LifecycleManager

manager = LifecycleManager()

def init_db():
    print("Initializing database...")

def cleanup_db():
    print("Closing database connections...")

# Lower priority values run first during startup
# Higher priority values run first during shutdown
manager.register_startup_hook(init_db,     priority=10)
manager.register_shutdown_hook(cleanup_db, priority=10)

manager.startup()

# Component health monitoring
class DatabaseComponent:
    def health_check(self):
        return {"healthy": True, "message": "Connected"}

manager.register_component("database", DatabaseComponent())
summary = manager.get_health_summary()
# → {"database": {"healthy": True, "message": "Connected"}, ...}

manager.shutdown(graceful=True)
```

## PluginRegistry

Register custom components that participate in the full pipeline:

```python
from semantica.core import PluginRegistry

class MyPlugin:
    def initialize(self):
        print("Plugin initialized")

    def execute(self, data):
        return {"processed": True}

registry = PluginRegistry(plugin_paths=["./plugins"])
registry.register_plugin(
    "my_plugin", MyPlugin,
    version="1.0.0",
    description="Custom domain extractor",
    author="team@example.com",
    capabilities=["extract"],
)

plugin = registry.load_plugin("my_plugin", api_key="xxx")
result = plugin.execute("sample data")

# Inspect registered plugins
for info in registry.list_plugins():
    print(f"{info['name']} v{info['version']} — {info['description']}")

# Unload when done
registry.unload_plugin("my_plugin")
```

## MethodRegistry

Register custom orchestration methods and dispatch them by name:

```python
from semantica.core import method_registry

def fast_kb_builder(sources, **kwargs):
    # Custom logic — skip embeddings for speed
    ...

method_registry.register("knowledge_base", "fast", fast_kb_builder)

from semantica.core.methods import build_knowledge_base
result = build_knowledge_base(sources=["doc.pdf"], method="fast")
```

## Schemas

<AccordionGroup>
  <Accordion title="SystemState enum">

```python
from semantica.core import SystemState

SystemState.UNINITIALIZED  # → startup() →
SystemState.INITIALIZING   # → hooks complete →
SystemState.READY          # → first operation →
SystemState.RUNNING        # → shutdown() →
SystemState.STOPPING       # → hooks complete →
SystemState.STOPPED
# Any unhandled exception during startup/shutdown →
SystemState.ERROR
```

Check current state at any time:

```python
state = manager.get_state()
if manager.is_ready():
    result = framework.build_knowledge_base(sources)
```

  </Accordion>
  <Accordion title="HealthStatus dataclass">

```python
@dataclass
class HealthStatus:
    component:  str             # component name
    healthy:    bool            # True = operational
    message:    str             # human-readable status
    timestamp:  datetime        # time of last check
    details:    Dict[str, Any]  # component-specific diagnostics
```

```python
health = manager.health_check()
for name, status in health.items():
    icon = "✓" if status.healthy else "✗"
    print(f"{icon} {name}: {status.message}")
```

  </Accordion>
  <Accordion title="PluginInfo and LoadedPlugin dataclasses">

```python
@dataclass
class PluginInfo:
    name:          str
    version:       str
    plugin_class:  Type
    description:   str
    author:        str
    dependencies:  List[str]    # pip package names required
    capabilities:  List[str]    # e.g. ["ingest", "extract"]
    metadata:      Dict[str, Any]

@dataclass
class LoadedPlugin:
    info:       PluginInfo
    instance:   Any             # the live plugin object
    config:     Dict[str, Any]  # config passed at load time
    loaded_at:  datetime
```

```python
registry = PluginRegistry()
registry.register_plugin("my_plugin", MyPlugin, version="1.0.0")

if registry.is_plugin_loaded("my_plugin"):
    plugin = registry.get_loaded_plugin("my_plugin")
else:
    plugin = registry.load_plugin("my_plugin")

details = registry.get_plugin_info("my_plugin")
```

  </Accordion>
</AccordionGroup>

## Complete Configuration Example

```yaml
# config.yaml
llm_provider:
  name: groq
  model: llama-3.3-70b-versatile
  api_key: ${GROQ_API_KEY}

embedding_model:
  provider: sentence-transformers
  model: all-mpnet-base-v2
  dimension: 768
  device: cpu               # "cpu" | "cuda" | "mps"

vector_store:
  backend: faiss
  dimension: 768
  index_type: hnsw          # "flat" | "ivf" | "hnsw" | "pq"

graph_db:
  backend: neo4j
  uri: bolt://localhost:7687
  user: neo4j
  password: ${NEO4J_PASSWORD}

processing:
  batch_size: 32
  max_workers: 4
  chunk_size: 512

pipeline:
  retry_max: 3
  backoff: exponential      # "fixed" | "linear" | "exponential"
  failure_strategy: skip    # "skip" | "stop" | "retry"

quality:
  min_confidence: 0.7
  dedup_threshold: 0.85

logging:
  level: INFO               # DEBUG | INFO | WARNING | ERROR
  format: "%(asctime)s %(name)s %(levelname)s %(message)s"
```

Load and use:

```python
from semantica.core import ConfigManager, Semantica

manager   = ConfigManager()
config    = manager.load_from_file("config.yaml")

config.set("processing.batch_size", 64)   # runtime override

framework = Semantica(config=config)
framework.initialize()
result    = framework.build_knowledge_base(["doc1.pdf", "doc2.docx"])
framework.shutdown()
```

## Tips and Common Pitfalls

<Tip>
  **Use individual modules directly unless you need application lifecycle management.** `Semantica` orchestrates the full pipeline, but for simple scripts and notebooks, using `FileIngestor`, `NERExtractor`, and `GraphBuilder` directly is clearer and more debuggable.
</Tip>

<Warning>
  **Always call `framework.shutdown(graceful=True)` in a `finally` block.** Without graceful shutdown, in-flight pipeline steps may leave partial writes in your vector store or graph database. Wrapping in `try/finally` guarantees cleanup even on exceptions.
</Warning>

<Tip>
  **Use `ConfigManager.merge_configs()` for environment-specific overrides.** Keep a `base.yaml` with default settings and a `prod.yaml` with overrides. Merge them at startup rather than maintaining separate copies — this prevents configuration drift between environments.
</Tip>

<Warning>
  **Environment variable overrides use double underscores for nesting.** `SEMANTICA_PROCESSING__BATCH_SIZE=64` sets `processing.batch_size` — the double underscore (`__`) represents a nesting level. A single underscore is reserved for multi-word keys within the same level.
</Warning>

<Tip>
  **Register startup hooks with explicit priorities.** `register_startup_hook(fn, priority=10)` — lower numbers run first. If your database hook (priority 10) must run before your cache hook (priority 20), those numbers guarantee the order. Without explicit priorities, execution order is undefined.
</Tip>

<Warning>
  **Check `manager.is_ready()` before running pipelines.** If `Semantica.initialize()` failed partway through (e.g., a database connection refused), the state transitions to `ERROR` rather than `READY`. Always check before submitting work to avoid errors that are hard to trace.
</Warning>

<CardGroup cols={2}>
  <Card title="Pipeline" icon="arrows-turn-to-dots" href="pipeline">
    Pipeline execution and step orchestration.
  </Card>
  <Card title="Utils" icon="wrench" href="utils">
    Shared utilities used by Core internally.
  </Card>
  <Card title="Getting Started" icon="play" href="../getting-started">
    Learn the basics before using Core.
  </Card>
  <Card title="LLMs" icon="microchip" href="llms">
    Configure LLM providers via ConfigManager.
  </Card>
</CardGroup>
