"""Docs integrity checker for PR #561."""
import json
import os
import re
import glob

DOCS_DIR = "docs"

results = {"pass": [], "fail": []}


def ok(msg):
    results["pass"].append(msg)
    print(f"  PASS  {msg}")


def fail(msg):
    results["fail"].append(msg)
    print(f"  FAIL  {msg}")


# ── 1. docs.json valid JSON ───────────────────────────────────────────────────
print("\n[1] docs.json validity")
try:
    with open(os.path.join(DOCS_DIR, "docs.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    ok("docs.json is valid JSON")
except Exception as e:
    fail(f"docs.json parse error: {e}")
    cfg = {}


# ── 2. All nav pages exist on disk ────────────────────────────────────────────
print("\n[2] Nav pages exist on disk")


def collect_pages(obj):
    pages = []
    if isinstance(obj, dict):
        if "pages" in obj:
            for p in obj["pages"]:
                if isinstance(p, str):
                    pages.append(p)
                else:
                    pages.extend(collect_pages(p))
        for v in obj.values():
            if isinstance(v, (dict, list)):
                pages.extend(collect_pages(v))
    elif isinstance(obj, list):
        for item in obj:
            pages.extend(collect_pages(item))
    return pages


nav_pages = [p for p in set(collect_pages(cfg)) if not p.startswith("http")]
missing_pages = []
for p in sorted(nav_pages):
    path = os.path.join(DOCS_DIR, p + ".md")
    if not os.path.exists(path):
        missing_pages.append(p)

if missing_pages:
    for m in missing_pages:
        fail(f"Nav page missing: {m}")
else:
    ok(f"All {len(nav_pages)} nav pages exist on disk")


# ── 3. Internal Card hrefs resolve (page-relative) ───────────────────────────
print("\n[3] Internal Card hrefs")
broken_hrefs = []

for fpath in glob.glob(DOCS_DIR + "/**/*.md", recursive=True):
    file_dir = os.path.dirname(fpath)
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    for m in re.finditer(r'href=["\'](?!http)([^"\'#]+)["\']', content):
        href = m.group(1).strip()
        if not href:
            continue
        # Resolve relative to the file's directory (mirrors browser URL resolution)
        resolved = os.path.normpath(os.path.join(file_dir, href))
        target_md = resolved + ".md"
        if not os.path.exists(target_md):
            rel = fpath.replace("\\", "/")
            broken_hrefs.append(f"{rel}: href '{href}' -> {target_md}")

if broken_hrefs:
    for b in broken_hrefs[:20]:
        fail(f"Broken href: {b}")
    if len(broken_hrefs) > 20:
        fail(f"...and {len(broken_hrefs) - 20} more broken hrefs")
else:
    ok("All internal Card hrefs resolve to real files")


# ── 4. No old repo URLs ───────────────────────────────────────────────────────
print("\n[4] Repo URL consistency")
old_patterns = ["Hawksight-AI/semantica", "semantica-dev/semantica"]
old_url_hits = []
for fpath in glob.glob(DOCS_DIR + "/**/*.md", recursive=True) + [
    os.path.join(DOCS_DIR, "docs.json")
]:
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    for pat in old_patterns:
        if pat in content:
            old_url_hits.append(f"{fpath}: contains '{pat}'")

if old_url_hits:
    for h in old_url_hits:
        fail(h)
else:
    ok("No old repo URLs found (Hawksight-AI, semantica-dev)")


# ── 5. All reference .md files have frontmatter ───────────────────────────────
print("\n[5] Reference page frontmatter")
ref_pages = list(glob.glob(DOCS_DIR + "/reference/*.md"))
no_frontmatter = []
for fpath in ref_pages:
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        no_frontmatter.append(os.path.basename(fpath))

if no_frontmatter:
    for f in no_frontmatter:
        fail(f"Missing frontmatter: {f}")
else:
    ok(f"All {len(ref_pages)} reference pages have frontmatter")


# ── 6. Code examples: no non-existent class names (exact word match) ──────────
print("\n[6] Known-wrong class names")
# (symbol, file, exclude_pattern) — exclude_pattern avoids substring false positives
banned = [
    ("BaseIngestor", "docs/architecture.md", None),
    ("BaseExtractor", "docs/architecture.md", None),
    ("BasePlugin", "docs/architecture.md", None),
    (r"PluginRegistry\.register\(", "docs/architecture.md", r"register_plugin"),
    ("start_explorer", "docs/reference/explorer.md", None),
    (r"graph\.save\(", "docs/reference/explorer.md", None),
    (r"\bDataNormalizer\b", "docs/reference/normalize.md", None),
    (r"\bEntityResolver\b", "docs/reference/deduplication.md", None),
    # ReasoningEngine: only flag as exact word, not as part of TemporalReasoningEngine
    (r"(?<!Temporal)(?<!Graph)\bReasoningEngine\b", "docs/reference/reasoning.md", None),
    (r"\bDeductiveEngine\b", "docs/reference/reasoning.md", None),
    (r"\bAbductiveEngine\b", "docs/reference/reasoning.md", None),
    (r"\bArangoExporter\b", "docs/reference/export.md", r"ArangoAQLExporter"),
    (r"\bGraphMLExporter\b", "docs/reference/export.md", None),
]
wrong_hits = []
for item in banned:
    symbol, fpath, exclude = item[0], item[1], item[2]
    if not os.path.exists(fpath):
        continue
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(symbol, content)
    if matches:
        # Apply exclusion filter
        if exclude:
            matches = [m for m in re.finditer(symbol, content)
                       if exclude not in content[max(0, m.start()-30):m.end()+30]]
            if not matches:
                continue
        wrong_hits.append(f"{fpath}: contains pattern '{symbol}'")

if wrong_hits:
    for w in wrong_hits:
        fail(w)
else:
    ok("No known-wrong class names in fixed reference pages")


# ── 7. Python 3.8 compat in docs snippets ─────────────────────────────────────
print("\n[7] Python 3.8 typing compatibility in docs code blocks")
# Only check inside ```python code blocks
py39_hits = []
in_code_block = False
for fpath in glob.glob(DOCS_DIR + "/**/*.md", recursive=True):
    with open(fpath, encoding="utf-8") as f:
        lines = f.readlines()
    in_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
        if in_block and re.search(r':\s*(list|dict|tuple|set)\[', line):
            rel = fpath.replace("\\", "/")
            py39_hits.append(f"{rel}:{i}: {line.rstrip()}")

if py39_hits:
    for h in py39_hits[:10]:
        fail(f"Py3.9+ syntax: {h}")
    if len(py39_hits) > 10:
        fail(f"...and {len(py39_hits) - 10} more")
else:
    ok("No Python 3.9+ lowercase generic type hints in doc code blocks")


# ── 8. Module table covers all 27 modules ─────────────────────────────────────
print("\n[8] Module table coverage in index.md")
expected_modules = [
    "semantica.ingest", "semantica.parse", "semantica.split", "semantica.normalize",
    "semantica.semantic_extract", "semantica.kg", "semantica.ontology", "semantica.reasoning",
    "semantica.embeddings", "semantica.vector_store", "semantica.graph_store", "semantica.triplet_store",
    "semantica.context", "semantica.provenance", "semantica.change_management",
    "semantica.deduplication", "semantica.conflicts", "semantica.export", "semantica.visualization",
    "semantica.pipeline", "semantica.seed", "semantica.llms", "semantica.mcp_server",
    "semantica.explorer", "semantica.evals", "semantica.utils", "semantica.core",
]
index_path = os.path.join(DOCS_DIR, "index.md")
with open(index_path, encoding="utf-8") as f:
    index_content = f.read()

missing_modules = [m for m in expected_modules if m not in index_content]
if missing_modules:
    for m in missing_modules:
        fail(f"Module missing from index table: {m}")
else:
    ok(f"All {len(expected_modules)} modules present in index.md table")


# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Results: {len(results['pass'])} passed, {len(results['fail'])} failed")
if results["fail"]:
    print("STATUS: FAIL")
    raise SystemExit(1)
else:
    print("STATUS: ALL CHECKS PASSED")
