---
title: "Ingest Module"
description: "Universal data ingestion from files, Parquet, XML, web, feeds, streams, repositories, email, and databases."
icon: "database"
---

`semantica.ingest` is the entry point for loading data into Semantica. Every ingestor returns a list of `DataSource` objects with normalized content and metadata, regardless of the original format.

## What You Get

<CardGroup cols={2}>
  <Card title="FileIngestor" icon="file">
    PDF, DOCX, HTML, JSON, CSV, Excel, PPTX, and ZIP/TAR archives — type auto-detected from extension.
  </Card>
  <Card title="ParquetIngestor" icon="table">
    PyArrow-based Parquet with Hive-style partition support and column selection (v0.5.0).
  </Card>
  <Card title="XMLIngestor" icon="code">
    XXE-safe lxml with XSD/DTD validation and directory scanning (v0.5.0).
  </Card>
  <Card title="StreamIngestor" icon="wave-square">
    Real-time ingestion from Kafka, RabbitMQ, AWS Kinesis, and Apache Pulsar.
  </Card>
  <Card title="Cloud Storage" icon="cloud">
    S3Ingestor, GCSIngestor, and GDriveIngestor with authentication options.
  </Card>
  <Card title="Database Ingestors" icon="database">
    DBIngestor, SnowflakeIngestor, MongoIngestor, and DuckDBIngestor.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Ingest local files">
    ```python
    from semantica.ingest import FileIngestor

    ingestor = FileIngestor()

    # Single file — type auto-detected from extension
    sources = ingestor.ingest("data/report.pdf")

    # Recursive directory scan
    sources = ingestor.ingest_directory("data/", recursive=True)

    # Glob pattern
    sources = ingestor.ingest("data/**/*.docx")
    ```
  </Step>
  <Step title="Connect to a remote source">
    ```python
    from semantica.ingest import DBIngestor

    ingestor = DBIngestor(
        connection_string="postgresql://user:pass@localhost/db",
        query="SELECT id, content, created_at FROM documents WHERE status='active'"
    )
    sources = ingestor.ingest()
    ```
  </Step>
  <Step title="Feed sources into the pipeline">
    ```python
    from semantica.pipeline import Pipeline
    from semantica.parse import DocumentParser
    from semantica.semantic_extract import NERExtractor
    from semantica.llms import Groq

    llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

    pipeline = Pipeline()
    pipeline.add_step("ingest",   FileIngestor())
    pipeline.add_step("parse",    DocumentParser())
    pipeline.add_step("extract",  NERExtractor(method="llm", llm_provider=llm))
    result = pipeline.run("data/")
    ```
  </Step>
</Steps>

## Ingestors

<Tabs>
  <Tab title="File-Based">
    ### FileIngestor

    ```python
    from semantica.ingest import FileIngestor

    ingestor = FileIngestor()
    sources  = ingestor.ingest("data/report.pdf")
    sources  = ingestor.ingest_directory("data/", recursive=True)
    sources  = ingestor.ingest("data/**/*.docx")
    ```

    Supported formats: PDF, DOCX, TXT, HTML, JSON, CSV, Excel (XLSX/XLS), PPTX, ZIP/TAR archives.

    ### ParquetIngestor (v0.5.0)

    PyArrow-based ingestion for Apache Parquet files, including Hive-style partitioned datasets:

    ```python
    from semantica.ingest import ParquetIngestor

    ingestor = ParquetIngestor()

    # Single Parquet file
    sources = ingestor.ingest("data/events.parquet")

    # Partitioned directory (year=2024/month=01/...)
    sources = ingestor.ingest("data/partitioned/")

    # Load only specific columns
    sources = ingestor.ingest("data/events.parquet", columns=["id", "text", "timestamp"])
    ```

    ### XMLIngestor (v0.5.0)

    XXE-safe lxml-based ingestion with optional schema validation:

    ```python
    from semantica.ingest import XMLIngestor

    ingestor = XMLIngestor()
    sources  = ingestor.ingest("data/records.xml")

    # With XSD validation
    ingestor = XMLIngestor(validate_xsd="schema.xsd")
    sources  = ingestor.ingest("data/records/")

    # With DTD validation
    ingestor = XMLIngestor(validate_dtd=True)
    sources  = ingestor.ingest("data/feed.xml")
    ```

    <Note>
      `XMLIngestor` uses lxml with `resolve_entities=False` to prevent XML External Entity (XXE) injection attacks.
    </Note>
  </Tab>
  <Tab title="Web & Feed">
    ### WebIngestor

    ```python
    from semantica.ingest import WebIngestor

    ingestor = WebIngestor(
        rate_limit=1.0,       # seconds between requests
        respect_robots=True,  # honor robots.txt
        max_depth=2           # crawl depth from seed URLs
    )

    sources = ingestor.ingest("https://example.com/about")
    sources = ingestor.ingest_urls([
        "https://example.com/page1",
        "https://example.com/page2",
    ])
    ```

    ### FeedIngestor (RSS/Atom)

    ```python
    from semantica.ingest import FeedIngestor

    ingestor = FeedIngestor()
    sources  = ingestor.ingest("https://feeds.example.com/rss")

    # Live monitoring — callback fires on new items
    ingestor.monitor(
        "https://feeds.example.com/rss",
        interval=300,
        callback=process_new_items
    )
    ```

    ### RepoIngestor

    Ingest Git repositories — source code, commit history, and dependency graphs:

    ```python
    from semantica.ingest import RepoIngestor

    ingestor = RepoIngestor(
        branch="main",
        file_types=[".py", ".md", ".yaml"],
        include_commits=True,
        commit_range="HEAD~100..HEAD",
    )

    sources = ingestor.ingest("https://github.com/org/repo")
    sources = ingestor.ingest("/path/to/local/repo")
    ```

    ### EmailIngestor

    Ingest emails via IMAP or POP3 with attachment extraction and thread analysis:

    ```python
    from semantica.ingest import EmailIngestor
    import os

    ingestor = EmailIngestor(
        protocol="imap",
        host="imap.gmail.com",
        port=993,
        use_ssl=True,
        username=os.getenv("EMAIL_USER"),
        password=os.getenv("EMAIL_PASS"),
        folder="INBOX",
        attachment_types=[".pdf", ".docx", ".txt"],
        include_thread_analysis=True,
        max_emails=500,
    )
    sources = ingestor.ingest()
    ```
  </Tab>
  <Tab title="Cloud Storage">
    ### S3Ingestor

    Ingest files directly from AWS S3 buckets:

    ```python
    from semantica.ingest import S3Ingestor
    import os

    ingestor = S3Ingestor(
        bucket="my-documents-bucket",
        prefix="reports/2024/",
        region="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        # Or omit credentials to use IAM instance profile
    )
    sources = ingestor.ingest()
    sources = ingestor.ingest(pattern="**/*.pdf")
    ```

    ### GCSIngestor

    Ingest files from Google Cloud Storage:

    ```python
    from semantica.ingest import GCSIngestor

    ingestor = GCSIngestor(
        bucket="my-gcs-bucket",
        prefix="data/",
        credentials_file="gcp-credentials.json",  # or use ADC
    )
    sources = ingestor.ingest()
    ```

    ### GDriveIngestor

    Ingest files from Google Drive folders via OAuth 2.0:

    ```python
    from semantica.ingest import GDriveIngestor

    ingestor = GDriveIngestor(
        credentials_file="oauth_credentials.json",
        token_file="token.json",
        folder_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs9",
        file_types=["pdf", "docx", "txt"],
        recursive=True,
    )
    sources = ingestor.ingest()
    ```
  </Tab>
  <Tab title="Database">
    ### DBIngestor (SQL)

    ```python
    from semantica.ingest import DBIngestor

    ingestor = DBIngestor(
        connection_string="postgresql://user:pass@localhost/db",
        query="SELECT id, content, created_at FROM documents WHERE status='active'"
    )
    sources = ingestor.ingest()
    ```

    ### SnowflakeIngestor

    ```python
    from semantica.ingest import SnowflakeIngestor
    import os

    ingestor = SnowflakeIngestor(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse="COMPUTE_WH",
        database="ANALYTICS",
        schema="PUBLIC"
    )
    sources = ingestor.ingest(query="SELECT * FROM documents")
    ```

    ### MongoIngestor

    Ingest documents from MongoDB collections:

    ```python
    from semantica.ingest import MongoIngestor
    import os

    ingestor = MongoIngestor(
        connection_string=os.getenv("MONGO_URI"),
        database="mydb",
        collection="articles",
        query={"status": "published", "year": {"$gte": 2022}},
        projection={"title": 1, "body": 1, "author": 1},
        content_field="body",
        limit=10000,
    )
    sources = ingestor.ingest()
    ```

    ### DuckDBIngestor

    Ingest data from DuckDB databases or directly from Parquet/CSV files via DuckDB SQL:

    ```python
    from semantica.ingest import DuckDBIngestor

    # In-memory DuckDB — query a Parquet file directly
    ingestor = DuckDBIngestor(
        query="SELECT id, text, created_at FROM read_parquet('data/*.parquet') WHERE year >= 2023",
    )
    sources = ingestor.ingest()

    # Persistent DuckDB database file
    ingestor = DuckDBIngestor(
        database_path="analytics.duckdb",
        query="SELECT doc_id AS id, content, metadata FROM documents",
        content_field="content",
    )
    sources = ingestor.ingest()
    ```
  </Tab>
  <Tab title="Stream">
    ### StreamIngestor

    Real-time ingestion from message brokers:

    ```python
    from semantica.ingest import StreamIngestor

    # Kafka
    ingestor = StreamIngestor(
        backend="kafka",
        bootstrap_servers="localhost:9092",
        topic="documents",
        group_id="semantica-consumer",
        auto_offset_reset="earliest",
    )
    sources = ingestor.ingest(max_messages=1000)

    # RabbitMQ
    ingestor = StreamIngestor(
        backend="rabbitmq",
        host="localhost",
        queue="document_queue",
        routing_key="docs.ingest",
        prefetch_count=100,
    )

    # AWS Kinesis
    ingestor = StreamIngestor(
        backend="kinesis",
        stream_name="documents-stream",
        region="us-east-1",
        shard_iterator_type="TRIM_HORIZON",
    )

    # Apache Pulsar
    ingestor = StreamIngestor(
        backend="pulsar",
        service_url="pulsar://localhost:6650",
        topic="persistent://public/default/documents",
        subscription_name="semantica-sub",
    )

    # Live monitoring — callback fires on each new message
    ingestor.monitor(callback=process_document, poll_interval=1.0)
    ```

    <Warning>
      Without a `max_messages` limit, `StreamIngestor.ingest()` blocks indefinitely waiting for new messages. Use `max_messages=1000` for batch processing; use `.monitor(callback=...)` for continuous streaming.
    </Warning>
  </Tab>
</Tabs>

## OntologyIngestor

Ingest existing OWL or RDF ontology files as structured knowledge sources:

```python
from semantica.ingest import OntologyIngestor

ingestor = OntologyIngestor(
    format="turtle",   # "turtle" | "xml" | "json-ld" | "nt" | "n3"
)

sources = ingestor.ingest("domain_ontology.owl")
sources = ingestor.ingest("ontologies/")
```

## DataSource Object

All ingestors return a list of `DataSource` objects with a consistent schema:

<Accordion title="DataSource schema">

```python
@dataclass
class DataSource:
    content:     str             # raw text content
    source_id:   str             # unique identifier
    source_type: str             # "file" | "web" | "database" | "stream" | ...
    metadata:    Dict            # title, author, url, date, page_count, etc.
    raw_bytes:   Optional[bytes] # original binary content if available
```

</Accordion>

## Custom Ingestors

Register a custom ingestor and it participates in the full pipeline:

```python
from semantica.ingest.registry import method_registry

def my_ingestor(source, **kwargs):
    return [{"content": "...", "metadata": {}, "source_id": source}]

method_registry.register("file", "my_format", my_ingestor)
```

## Tips and Common Pitfalls

<Tip>
  **`FileIngestor` is always the fastest path for local files.** It auto-detects format from extension, handles ZIP/TAR archives automatically, and supports glob patterns. Only reach for `DoclingParser` when `DocumentParser` can't handle your layout.
</Tip>

<Tip>
  **Use `ParquetIngestor` instead of `FileIngestor` for structured analytical data.** Parquet ingestion preserves column types (int, float, datetime) that CSV reading loses. Use `columns=["id", "text"]` to avoid loading unused columns — critical for wide tables with hundreds of columns.
</Tip>

<Warning>
  **`XMLIngestor` is XXE-safe by default.** Do not use standard `xml.etree.ElementTree` to pre-parse XML before passing to Semantica — it doesn't block XXE attacks. `XMLIngestor` uses lxml with `resolve_entities=False` to safely parse untrusted XML.
</Warning>

<Warning>
  **Stream ingestors need explicit `max_messages` for batch runs.** Without a limit, `StreamIngestor.ingest()` blocks indefinitely waiting for new messages. Use `max_messages=1000` for batch processing; use `.monitor(callback=...)` for continuous streaming.
</Warning>

<Tip>
  **Rate-limit web crawling.** `WebIngestor(rate_limit=1.0, respect_robots=True)` is the responsible default. Without rate limiting, you risk getting blocked by the target server or violating its terms of service.
</Tip>

<Tip>
  **All ingestors return the same `DataSource` schema.** This means you can mix sources in a single pipeline without any adapter code — `FileIngestor`, `MongoIngestor`, and `StreamIngestor` outputs are all directly composable with `DocumentParser` and `NERExtractor`.
</Tip>

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse raw sources into structured text and tables.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Orchestrate ingest as the first pipeline step.
  </Card>
  <Card title="Snowflake Integration" icon="snowflake" href="../integrations/snowflake">
    Snowflake-specific setup and authentication guide.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Track lineage from ingest through to inference.
  </Card>
</CardGroup>
