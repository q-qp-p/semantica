---
title: "Parse Module"
description: "Document parsing and text extraction — DocumentParser for standard formats and DoclingParser for complex layouts."
icon: "file-lines"
---

`semantica.parse` extracts structured text, layout, tables, and metadata from unstructured documents. `DocumentParser` handles clean machine-readable files; `DoclingParser` handles complex layouts, scanned PDFs, and multi-column documents.

## What You Get

<CardGroup cols={2}>
  <Card title="DocumentParser" icon="file-lines">
    Standard parser for PDF, DOCX, HTML, TXT, JSON, CSV, PPTX, XLSX — zero config, no extras.
  </Card>
  <Card title="DoclingParser" icon="file-pdf">
    Advanced parser for complex layouts, merged-cell tables, multi-column PDFs, and OCR.
  </Card>
  <Card title="CodeParser" icon="code">
    AST structure extraction — functions, classes, imports, dependencies — for 10+ languages.
  </Card>
  <Card title="ImageParser" icon="image">
    EXIF metadata extraction and OCR via Tesseract for image files.
  </Card>
  <Card title="MediaParser" icon="photo-film">
    Technical metadata from audio, video, and image files (duration, codec, resolution).
  </Card>
  <Card title="MCPParser" icon="plug">
    Parse Model Context Protocol responses into structured `ParsedDocument` objects.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Parse a standard document">
    ```python
    from semantica.parse import DocumentParser

    parser = DocumentParser()
    parsed = parser.parse("data/report.pdf")

    print(parsed.text)       # full clean text
    print(parsed.metadata)   # title, author, date, page_count, language, etc.
    print(parsed.sections)   # document structure as a list of Section objects
    ```
  </Step>
  <Step title="Use DoclingParser for complex layouts">
    ```bash
    pip install "semantica[docling]"
    ```

    ```python
    from semantica.parse import DoclingParser

    parser = DoclingParser(
        extract_tables=True,       # structured table extraction with cell type detection
        extract_images=True,       # extract image regions for downstream OCR
        output_format="markdown",  # "markdown" | "html" | "json"
    )

    parsed = parser.parse("data/annual_report.pdf")
    print(parsed.tables)   # structured TableData objects with headers and rows
    ```
  </Step>
  <Step title="Feed into the split and extract pipeline">
    ```python
    from semantica.split import TextSplitter
    from semantica.semantic_extract import NERExtractor
    from semantica.llms import Groq
    import os

    splitter = TextSplitter(method="structural")
    chunks   = splitter.split_document(parsed)

    llm       = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    extractor = NERExtractor(method="llm", llm_provider=llm)
    entities  = extractor.extract_batch([c.text for c in chunks])
    ```
  </Step>
</Steps>

## Parser Reference

<Tabs>
  <Tab title="DocumentParser">
    Standard parser for clean, machine-readable documents — no extra dependencies required:

    ```python
    from semantica.parse import DocumentParser

    parser = DocumentParser()
    parsed = parser.parse("data/report.pdf")

    print(parsed.text)       # full clean text
    print(parsed.metadata)   # title, author, date, page_count, language, etc.
    print(parsed.sections)   # document structure as a list of Section objects
    ```

    **Supported formats:** PDF, DOCX, HTML, TXT, JSON, CSV, PPTX, XLSX.
  </Tab>
  <Tab title="DoclingParser">
    Advanced parser using the Docling backend — handles layouts that `DocumentParser` cannot:

    ```python
    from semantica.parse import DoclingParser

    parser = DoclingParser(
        extract_tables=True,       # structured table extraction with cell type detection
        extract_images=True,       # extract image regions for downstream OCR
        output_format="markdown",  # "markdown" | "html" | "json"
    )

    parsed = parser.parse("data/annual_report.pdf")
    print(parsed.tables)    # structured TableData objects with headers and rows
    print(parsed.sections)  # document structure with heading hierarchy
    ```

    **Use `DoclingParser` for:**
    - Multi-column PDF layouts
    - Tables with merged cells or complex headers
    - PPTX slides with embedded charts
    - XLSX spreadsheets with formulas
    - Scanned documents with OCR
    - Academic papers and technical reports

    **OCR support:**

    ```python
    parser = DoclingParser(
        ocr=True,
        ocr_language=["en"],   # ISO 639-1 codes; list for multi-language documents
        extract_tables=True,
    )
    parsed = parser.parse("data/scanned_contract.pdf")
    ```
  </Tab>
  <Tab title="CodeParser">
    Parse source code files — extracts AST structure, functions, classes, imports, and comments:

    ```python
    from semantica.parse import CodeParser

    parser = CodeParser(
        extract_comments=True,       # include docstrings and inline comments
        extract_dependencies=True,   # import/require statements
        language="auto",             # "auto" | "python" | "javascript" | "java" | "go" | "rust" | "cpp"
    )

    parsed = parser.parse("src/main.py")

    print(parsed.text)                      # raw source code as text
    print(parsed.metadata["language"])      # detected language
    print(parsed.metadata["functions"])     # list of function names
    print(parsed.metadata["classes"])       # list of class names
    print(parsed.metadata["imports"])       # list of import statements
    print(parsed.metadata["comments"])      # docstrings and inline comments
    ```

    **Supported languages:** Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, C#, Ruby, PHP, Swift.
  </Tab>
  <Tab title="ImageParser">
    Extract EXIF metadata and optionally perform OCR on image files:

    ```python
    from semantica.parse import ImageParser

    parser = ImageParser(
        extract_exif=True,   # camera, GPS, timestamps, etc.
        ocr=True,            # OCR via Tesseract (requires tesseract-ocr installed)
        ocr_language="en",   # ISO 639-1 language code for OCR
    )

    parsed = parser.parse("photo.jpg")

    print(parsed.text)                        # OCR-extracted text (if ocr=True)
    print(parsed.metadata["width"])           # image dimensions
    print(parsed.metadata["height"])
    print(parsed.metadata["format"])          # "JPEG" | "PNG" | "TIFF" | ...
    print(parsed.metadata["exif"]["GPS"])     # GPS coordinates if available
    print(parsed.metadata["exif"]["DateTime"])
    ```
  </Tab>
  <Tab title="MediaParser & MCPParser">
    ### MediaParser

    Extract technical metadata from audio, video, and image files:

    ```python
    from semantica.parse import MediaParser

    parser = MediaParser()

    # Video file
    parsed = parser.parse("interview.mp4")
    print(parsed.metadata["duration_seconds"])
    print(parsed.metadata["codec"])
    print(parsed.metadata["resolution"])
    print(parsed.metadata["fps"])

    # Audio file
    parsed = parser.parse("podcast.mp3")
    print(parsed.metadata["duration_seconds"])
    print(parsed.metadata["bitrate"])
    print(parsed.metadata["channels"])
    ```

    **Supported formats:** MP4, AVI, MOV, MKV, MP3, WAV, FLAC, OGG, JPEG, PNG, TIFF, WebP.

    ### MCPParser

    Parse Model Context Protocol (MCP) responses into structured `ParsedDocument` objects:

    ```python
    from semantica.parse import MCPParser

    parser = MCPParser()

    mcp_response = {
        "content": [{"type": "text", "text": "Apple Inc. was founded in 1976..."}],
        "metadata": {"tool": "web_search", "query": "Apple Inc history"}
    }

    parsed = parser.parse(mcp_response)
    print(parsed.text)      # "Apple Inc. was founded in 1976..."
    print(parsed.metadata)  # tool name, query, and other MCP metadata
    ```
  </Tab>
</Tabs>

## Parsed Document Schema

<AccordionGroup>
  <Accordion title="ParsedDocument dataclass">

```python
@dataclass
class ParsedDocument:
    text:      str                  # full extracted text
    sections:  List[Section]        # heading-based document structure
    tables:    List[TableData]      # structured table data (DoclingParser only)
    metadata:  DocumentMetadata     # title, author, dates, page count
    source_id: str                  # links back to the original DataSource
```

  </Accordion>
  <Accordion title="DocumentMetadata dataclass">

```python
@dataclass
class DocumentMetadata:
    title:        Optional[str]
    author:       Optional[str]
    created_date: Optional[datetime]
    page_count:   int
    language:     Optional[str]     # ISO 639-1 code
    has_tables:   bool
    has_images:   bool
    word_count:   int
    format:       str               # "pdf" | "docx" | "pptx" | ...
```

  </Accordion>
</AccordionGroup>

## Choosing a Parser

| Scenario | Parser |
| -------- | ------ |
| Clean PDFs, DOCX, HTML, TXT, CSV, Excel | `DocumentParser` — zero config, no extras |
| Scanned PDFs, OCR required | `DoclingParser(ocr=True)` — requires `pip install "semantica[docling]"` |
| Multi-column PDFs, merged-cell tables | `DoclingParser(extract_tables=True)` |
| Source code files | `CodeParser(language="auto")` |
| Images with embedded text | `ImageParser(ocr=True)` — requires Tesseract |
| Audio/video metadata | `MediaParser()` |
| MCP tool responses | `MCPParser()` |

## Integration with FileIngestor

The most common pattern — ingest a directory then parse each source:

```python
from semantica.ingest import FileIngestor
from semantica.parse import DoclingParser

ingestor = FileIngestor()
parser   = DoclingParser(extract_tables=True)

sources = ingestor.ingest("data/reports/")
for source in sources:
    parsed = parser.parse(source)
    # → parsed.text, parsed.tables, parsed.sections
```

<Note>
  Docling is an optional dependency. If `docling` is not installed, `DoclingParser` raises an `ImportError` with installation instructions. `DocumentParser` is always available and requires no extras.
</Note>

## Tips and Common Pitfalls

<Tip>
  **Start with `DocumentParser` and only switch to `DoclingParser` when needed.** `DoclingParser` is significantly more powerful but slower and requires an additional dependency. For clean machine-readable PDFs and Office files, `DocumentParser` is fast and accurate enough.
</Tip>

<Warning>
  **OCR requires Tesseract installed on the system.** `ImageParser(ocr=True)` and `DoclingParser(ocr=True)` both call Tesseract under the hood. Install it with `apt-get install tesseract-ocr` (Linux) or `brew install tesseract` (macOS) before enabling OCR.
</Warning>

<Tip>
  **`extract_tables=True` is off by default for speed.** Table extraction in `DoclingParser` requires additional layout analysis passes. Only enable it when you actually need structured table data — for text-only extraction, leave it off.
</Tip>

<Tip>
  **`CodeParser` outputs AST metadata, not just raw text.** The `parsed.metadata["functions"]` and `parsed.metadata["classes"]` lists are useful for building code-level knowledge graphs — function call graphs, class inheritance hierarchies, dependency graphs.
</Tip>

<Warning>
  **Always pass the `ParsedDocument` to `TextSplitter` before extraction.** Raw `parsed.text` is a flat string. Use `TextSplitter` to chunk it into semantically meaningful pieces before running NER — this dramatically reduces context window overflow on large documents.
</Warning>

<CardGroup cols={2}>
  <Card title="Ingest" icon="database" href="ingest">
    Load files before parsing.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk parsed text for embedding and extraction.
  </Card>
  <Card title="Docling Integration" icon="file-pdf" href="../integrations/docling">
    Full Docling integration setup guide.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extract entities and relations from parsed text.
  </Card>
</CardGroup>
