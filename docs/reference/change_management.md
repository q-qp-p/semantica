---
title: "Change Management Module"
description: "Version control, SHA-256 checksums, diff analysis, rollback, and audit trails for knowledge graphs and ontologies."
icon: "clock-rotate-left"
---

> Enterprise-grade version control and audit trails for knowledge graphs with data integrity verification.

---

## Overview

The **Change Management Module** provides versioning for knowledge graphs — SHA-256 checksums, full snapshot history, diff analysis, rollback protection, and compliance-grade audit trails (HIPAA, SOX, FDA 21 CFR Part 11).

<CardGroup cols={2}>
  <Card title="TemporalVersionManager" icon="clock">
    Snapshot, diff, rollback, and audit trail for knowledge graphs.
  </Card>
  <Card title="OntologyVersionManager" icon="sitemap">
    Version control for OWL ontologies with diff and migration support.
  </Card>
  <Card title="VersionStorage" icon="database">
    Pluggable storage — in-memory for tests, SQLite for production.
  </Card>
  <Card title="Integrity Verification" icon="shield-check">
    SHA-256 checksums to detect unauthorized modifications.
  </Card>
</CardGroup>

---

## TemporalVersionManager

Version control for knowledge graphs:

```python
from semantica.change_management import TemporalVersionManager

manager = TemporalVersionManager(storage_path="versions.db")

# Create a snapshot
snapshot_id = manager.create_snapshot(
    graph=kg,
    version="v1.0",
    author="user@example.com",
    message="Initial knowledge graph"
)

print(f"Snapshot {snapshot_id}")
print(f"Checksum: {manager.get_checksum(snapshot_id)}")
```

---

## Versioning

```python
# List all versions
versions = manager.list_versions()
for v in versions:
    print(f"{v.version} — {v.author} — {v.created_at} — {v.checksum[:8]}...")

# Retrieve a specific version
kg_v1 = manager.get_version("v1.0")

# Rollback
manager.rollback(target_version="v1.0", allow_data_loss=False)
```

---

## Diff Analysis

```python
diff = manager.diff("v1.0", "v2.0")

print(f"Added nodes:    {len(diff.added_nodes)}")
print(f"Removed nodes:  {len(diff.removed_nodes)}")
print(f"Modified edges: {len(diff.modified_edges)}")

for change in diff.changes:
    print(f"  [{change.type}] {change.element}: {change.description}")
```

---

## OntologyVersionManager

Version control for OWL ontologies:

```python
from semantica.change_management import OntologyVersionManager, OntologyVersion

manager = OntologyVersionManager()

# Save a version
version: OntologyVersion = manager.save_version(
    ontology=ontology,
    version="1.2.0",
    author="ontology-team",
    message="Added FHIR alignment mappings"
)

# Diff two ontology versions
diff = manager.diff("1.1.0", "1.2.0")
for change in diff.changes:
    print(f"[{change.type}] {change.class_name}: {change.description}")
```

---

## VersionStorage

Pluggable storage backends:

```python
from semantica.change_management import (
    VersionStorage,
    InMemoryVersionStorage,
    SQLiteVersionStorage,
)

# In-memory (tests and development)
storage = InMemoryVersionStorage()

# SQLite (production — persistent across restarts)
storage = SQLiteVersionStorage(db_path="versions.db")

# Pass to a version manager
manager = TemporalVersionManager(storage=storage)
```

---

## Integrity Verification

SHA-256 checksums detect any unauthorized modification to the graph:

```python
from semantica.change_management import compute_checksum, verify_checksum

# Compute checksum for a graph
checksum = compute_checksum(kg)

# Verify graph against stored checksum
is_valid = verify_checksum(kg, expected_checksum=checksum)

if not is_valid:
    print("Warning: Graph has been modified since the checksum was recorded")
```

---

## Audit Trail

```python
# Full audit trail for an entity
trail = manager.get_audit_trail(entity_id="apple_inc")
for entry in trail:
    print(f"{entry.timestamp} — {entry.author}: {entry.action} — {entry.description}")

# Export audit trail
manager.export_audit_trail("audit.csv",  format="csv")
manager.export_audit_trail("audit.json", format="json")
```

---

## ChangeLogEntry

Every version snapshot includes a structured `ChangeLogEntry`:

```python
from semantica.change_management import ChangeLogEntry

entry: ChangeLogEntry = manager.get_log_entry(snapshot_id)

print(entry.version)
print(entry.author)
print(entry.message)
print(entry.checksum)
print(entry.created_at)
print(entry.changes)    # list of individual change records
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Provenance" icon="link" href="provenance">
    W3C PROV-O lineage tracking.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being versioned.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Export versioned snapshots.
  </Card>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Detect conflicts introduced between versions.
  </Card>
</CardGroup>
