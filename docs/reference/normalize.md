---
title: "Normalize Module"
description: "Text cleaning, entity canonicalization, date normalization, number/unit conversion, language detection, and encoding repair."
icon: "broom"
---

> Clean, standardize, and prepare text and data for semantic processing.

---

## Overview

The **Normalize Module** standardizes raw data before extraction and graph construction — fixing encodings, canonicalizing entity names, normalizing dates, and detecting languages. All normalizers expose both convenience functions and stateful class instances.

<CardGroup cols={2}>
  <Card title="TextNormalizer" icon="text-size">
    Unicode, whitespace, HTML stripping, smart-quote/dash replacement.
  </Card>
  <Card title="EntityNormalizer" icon="user-check">
    Alias resolution, disambiguation, name variant handling.
  </Card>
  <Card title="DateNormalizer" icon="calendar">
    ISO 8601 output, timezone conversion, relative date parsing.
  </Card>
  <Card title="NumberNormalizer" icon="hashtag">
    Currency, unit conversion, scientific notation.
  </Card>
  <Card title="DataCleaner" icon="broom">
    Duplicate detection, schema validation, missing value handling.
  </Card>
  <Card title="LanguageDetector" icon="globe">
    50+ language detection with confidence scoring.
  </Card>
</CardGroup>

---

## Convenience Functions

The quickest way to normalize — dispatch via function with a `method` parameter:

```python
from semantica.normalize import (
    normalize_text, normalize_entity, normalize_date,
    normalize_number, clean_data, detect_language, handle_encoding
)

clean  = normalize_text("  Hello,   World!!  \n\n")
# → "Hello, World!!"

entity = normalize_entity("Apple Computer Inc.", entity_type="Organization")
# → "Apple Inc."

date   = normalize_date("Jan 1st, 2020")
# → "2020-01-01"

num    = normalize_number("$1,234.56")
# → 1234.56

lang   = detect_language("Bonjour le monde")
# → {"language": "fr", "confidence": 0.98}
```

---

## TextNormalizer

```python
from semantica.normalize import TextNormalizer

normalizer = TextNormalizer()

normalized = normalizer.normalize_text(
    raw_text,
    lowercase=False,
    remove_punctuation=False,
    remove_extra_whitespace=True,
    strip_html=True,            # remove HTML tags
    normalize_unicode=True,     # NFC normalization
)
```

<AccordionGroup>

<Accordion title="UnicodeNormalizer — NFC/NFD/NFKC/NFKD forms" icon="font">

```python
from semantica.normalize import UnicodeNormalizer

normalizer = UnicodeNormalizer(form="NFC")
text = normalizer.normalize("café")   # NFC → canonical composition
```

</Accordion>

<Accordion title="WhitespaceNormalizer — tabs, line breaks, extra spaces" icon="align-left">

```python
from semantica.normalize import WhitespaceNormalizer

normalizer = WhitespaceNormalizer()
text = normalizer.normalize("Hello   World\t\n")  # → "Hello World"
```

</Accordion>

<Accordion title="SpecialCharacterProcessor — smart quotes, dashes, ellipsis" icon="quote-right">

```python
from semantica.normalize import SpecialCharacterProcessor

processor = SpecialCharacterProcessor()
text = processor.process("‘Hello’")  # '' → ''
```

</Accordion>

</AccordionGroup>

<Note>
  **v0.5.0 fix:** Encoding repair now handles cp1252/latin-1 characters that previously caused crashes on Windows when processing documents with non-ASCII content.
</Note>

---

## EntityNormalizer

```python
from semantica.normalize import EntityNormalizer

normalizer = EntityNormalizer()

# Normalize company names — handles suffixes, punctuation, case
companies = ["Apple Computer, Inc.", "Apple Inc", "APPLE INC."]
normalized = [normalizer.normalize_entity(c) for c in companies]
# All → "Apple Inc."

# Person names
name = normalizer.normalize_entity("JOBS, STEVE", entity_type="Person")
# → "Steve Jobs"
```

<AccordionGroup>

<Accordion title="AliasResolver — dictionary-based alias mapping" icon="arrow-right-arrow-left">

```python
from semantica.normalize import AliasResolver

resolver = AliasResolver(aliases={
    "ML": "Machine Learning",
    "AI": "Artificial Intelligence",
    "DL": "Deep Learning",
})

resolved = resolver.resolve("ML and DL are subsets of AI")
# → "Machine Learning and Deep Learning are subsets of Artificial Intelligence"
```

</Accordion>

<Accordion title="EntityDisambiguator — context-aware disambiguation" icon="arrows-split-up-and-left">

```python
from semantica.normalize import EntityDisambiguator

disambiguator = EntityDisambiguator()
result = disambiguator.disambiguate(
    "Apple", context="Steve Jobs founded Apple in Cupertino"
)
# → {"entity": "Apple Inc.", "type": "Organization", "confidence": 0.96}
```

</Accordion>

<Accordion title="NameVariantHandler — honorifics, titles, cultural variants" icon="id-card">

```python
from semantica.normalize import NameVariantHandler

handler = NameVariantHandler()
canonical = handler.normalize("Dr. JOHN P. SMITH Jr.")
# → "John P. Smith"
```

</Accordion>

</AccordionGroup>

---

## DateNormalizer

```python
from semantica.normalize import DateNormalizer

normalizer = DateNormalizer()

dates = [
    "January 1st, 2020",
    "01/01/2020",
    "2020-01-01T00:00:00Z",
    "yesterday",        # relative dates supported
    "3 weeks ago",
]
normalized = [normalizer.normalize_date(d) for d in dates]
# All → ISO 8601 strings

# With timezone conversion to UTC
normalizer_utc = DateNormalizer(target_timezone="UTC")
utc_date = normalizer_utc.normalize_date("2024-01-01 09:00 EST")
```

<AccordionGroup>

<Accordion title="TimeZoneNormalizer" icon="clock">

```python
from semantica.normalize import TimeZoneNormalizer

tz_normalizer = TimeZoneNormalizer(target_tz="UTC")
utc_dt = tz_normalizer.normalize("2024-01-01 09:00", source_tz="America/New_York")
```

</Accordion>

<Accordion title="RelativeDateProcessor — 'yesterday', '3 weeks ago'" icon="calendar-days">

```python
from semantica.normalize import RelativeDateProcessor
from datetime import datetime

processor = RelativeDateProcessor(reference_date=datetime(2025, 1, 15))
result = processor.process("3 days ago")
# → datetime(2025, 1, 12)
```

</Accordion>

<Accordion title="TemporalExpressionParser — date ranges and complex expressions" icon="calendar-range">

```python
from semantica.normalize import TemporalExpressionParser

parser = TemporalExpressionParser()
result = parser.parse("from January 2020 to March 2021")
# → {"start": "2020-01-01", "end": "2021-03-31", "type": "range"}
```

</Accordion>

</AccordionGroup>

---

## NumberNormalizer

```python
from semantica.normalize import NumberNormalizer

normalizer = NumberNormalizer()

# Currency
normalizer.normalize_number("$1,234.56")    # → 1234.56
normalizer.normalize_number("€42K")          # → 42000.0
normalizer.normalize_number("$1.2B")         # → 1200000000.0

# Scientific notation
normalizer.normalize_number("3.14e-2")       # → 0.0314

# Percentages
normalizer.normalize_number("42%")           # → 0.42
```

<AccordionGroup>

<Accordion title="UnitConverter — length, weight, volume, temperature" icon="ruler">

```python
from semantica.normalize import UnitConverter

converter = UnitConverter()
result = converter.convert(100, from_unit="km/h", to_unit="m/s")
# → 27.78

# All supported categories: length, weight, volume, temperature, speed, area
categories = converter.list_categories()
```

</Accordion>

<Accordion title="CurrencyNormalizer — symbol/code resolution" icon="dollar-sign">

```python
from semantica.normalize import CurrencyNormalizer

normalizer = CurrencyNormalizer()
result = normalizer.normalize("$42.50")
# → {"amount": 42.50, "currency": "USD", "raw": "$42.50"}
```

</Accordion>

</AccordionGroup>

---

## DataCleaner

```python
from semantica.normalize import DataCleaner, DataValidator, DuplicateDetector

cleaner = DataCleaner()

# Remove duplicates from a dataset
deduped = cleaner.remove_duplicates(records, similarity_threshold=0.9)

# Fill missing values
filled = cleaner.fill_missing(records, strategy="mean")  # or "median", "mode", "remove"

# Validate schema
validator = DataValidator()
result = validator.validate(records, schema={"name": str, "age": int})
print(result.valid_count, result.errors)
```

---

## LanguageDetector

```python
from semantica.normalize import LanguageDetector

detector = LanguageDetector()

# Single text
lang = detector.detect("Bonjour le monde")
# → {"language": "fr", "confidence": 0.98}

# Top N languages
langs = detector.detect_top_n("This might be mixed", n=3)
# → [{"language": "en", "probability": 0.85}, ...]

# Batch
results = detector.detect_batch(["Hello", "Hola", "Bonjour"])
```

---

## EncodingHandler

```python
from semantica.normalize import EncodingHandler

handler = EncodingHandler()

# Detect encoding
encoding = handler.detect_encoding(raw_bytes)
# → {"encoding": "windows-1252", "confidence": 0.73}

# Convert to UTF-8
utf8_text = handler.to_utf8(raw_bytes)

# Remove BOM
clean = handler.remove_bom(text_with_bom)
```

---

## Batch Processing

All normalizers support batch input:

```python
from semantica.normalize import normalize_text

texts = ["Text 1...", "Text 2...", "Text 3..."]
normalized = [normalize_text(t) for t in texts]
```

For large datasets, use the pipeline:

```python
from semantica.pipeline import Pipeline
from semantica.normalize import TextNormalizer

pipeline = Pipeline()
pipeline.add_step("normalize", TextNormalizer())
result = pipeline.run(documents)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse documents before normalization.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk normalized text.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Resolve duplicate entities post-normalization.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Include normalization in a pipeline.
  </Card>
</CardGroup>
