#!/usr/bin/env python3

"""
pdf_parser.py

Layout-aware extraction of Results / results-like main-body text from scientific PDFs.

Key features
------------
1. Conventional papers:
       Results -> Discussion

2. Combined sections:
       Results and Discussion -> back matter

3. Nature-style papers without an explicit Results heading:
       first genuine body subsection heading -> Discussion
   If Discussion is absent:
       first genuine body subsection heading -> back matter / end of article

4. Multi-column handling:
   - PyMuPDF's sort=True can interleave two/three-column text because it sorts
     primarily by page coordinates.
   - This script detects multi-column pages and uses native PDF content order
     (sort=False) on those pages.
   - Single-column pages use sort=True.

5. Cleans common PDF extraction artefacts while preserving scientific notation.

6. Removes isolated single-character / figure-panel / axis-label fragments from
   JSON and TXT output.

7. Splits mixed blocks where a bold subsection heading and normal body text were
   merged by the PDF parser.

8. Learns the manuscript body font profile and removes text embedded inside
   figures/diagrams. Figure and table captions/legends are also removed.

Install
-------
pip install pymupdf

Usage
-----
python pdf_parser.py paper.pdf
python pdf_parser.py /path/to/pdf_folder --cores 8
python pdf_parser.py /path/to/pdf_folder --threads 8 --outdir extracted_results
"""

import argparse
import json
import os
import re
import hashlib
import unicodedata
from pathlib import Path
from statistics import median
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

import pymupdf as fitz  # PyMuPDF (current API)



# ============================================================
# DOI HASH RESOLUTION
# ============================================================

DOI_RE = re.compile(
    r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",
    flags=re.IGNORECASE,
)


def generate_doi_hash(doi: str) -> str:
    """Generate the 16-character SHA-256 DOI hash used for PDF filenames."""
    return hashlib.sha256(doi.encode("utf-8")).hexdigest()[:16]


def normalize_doi(doi: str) -> str:
    """
    Normalize a DOI extracted from PDF text/metadata.

    This does NOT alter internal DOI punctuation. It only removes common
    wrappers/prefixes and trailing sentence punctuation introduced by prose.
    """
    if not doi:
        return ""

    doi = unicodedata.normalize("NFKC", str(doi)).strip()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = re.sub(r"^doi\s*:\s*", "", doi, flags=re.IGNORECASE)
    doi = doi.strip()

    # Remove punctuation that is very commonly attached by sentence prose.
    doi = doi.rstrip(".,;:")

    # Remove unmatched closing brackets at the very end, while preserving DOI
    # suffixes that legitimately contain balanced parentheses.
    while doi.endswith(")") and doi.count(")") > doi.count("("):
        doi = doi[:-1]
    while doi.endswith("]") and doi.count("]") > doi.count("["):
        doi = doi[:-1]
    while doi.endswith("}") and doi.count("}") > doi.count("{"):
        doi = doi[:-1]

    return doi.strip()


def doi_hash_matches(doi: str, expected_hash: str) -> bool:
    """
    Check an extracted DOI against the hash encoded in the PDF filename.

    DOI names are case-insensitive in normal use, while SHA-256 is not. We
    therefore test both the extracted form and its lowercase canonical form.
    """
    doi = normalize_doi(doi)
    expected_hash = expected_hash.lower()

    if not doi:
        return False

    candidates = [doi]
    lower = doi.lower()
    if lower != doi:
        candidates.append(lower)

    return any(generate_doi_hash(x) == expected_hash for x in candidates)


def _doi_candidates_from_text(text: str):
    """Yield normalized DOI candidates from arbitrary PDF text."""
    if not text:
        return

    for match in DOI_RE.finditer(text):
        doi = normalize_doi(match.group(0))
        if doi:
            yield doi


def resolve_doi_from_hashed_pdf(pdf_file):
    """
    Recover the DOI associated with a hash-named PDF.

    Important: SHA-256 hashes cannot be mathematically reversed. Instead, this
    function extracts DOI candidates from the PDF itself and identifies the DOI
    whose SHA-256 prefix reproduces the filename hash.

    Example
    -------
    filename: 963c9a2bd4de6809.pdf
    PDF contains: 10.1016/j.cell.2019.11.037
    SHA256(...)[0:16] == 963c9a2bd4de6809

    Returns
    -------
    str | None
        Full DOI URL, e.g. https://doi.org/10.1016/j.cell.2019.11.037,
        or None if no hash-matching DOI can be found.
    """
    pdf_file = Path(pdf_file)
    expected_hash = pdf_file.stem.lower()

    # Only attempt hash resolution for names that look like the 16-char hash
    # produced by generate_doi_hash().
    if not re.fullmatch(r"[0-9a-f]{16}", expected_hash):
        return None

    doc = fitz.open(pdf_file)
    try:
        # 1. Search PDF metadata first (fast and sometimes authoritative).
        metadata = doc.metadata or {}
        for value in metadata.values():
            if not value:
                continue
            for doi in _doi_candidates_from_text(str(value)):
                if doi_hash_matches(doi, expected_hash):
                    return "https://doi.org/" + doi.lower()

        # 2. Search page text sequentially. We stop immediately on the first
        # hash match, so references containing unrelated DOIs are harmless.
        for page in doc:
            page_text = page.get_text("text", sort=False)
            for doi in _doi_candidates_from_text(page_text):
                if doi_hash_matches(doi, expected_hash):
                    return "https://doi.org/" + doi.lower()

    finally:
        doc.close()

    return None


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_HEADINGS = [
    r"results",
    r"results\s+and\s+discussion",
    r"results\s+and\s+discussions",
]

DISCUSSION_HEADINGS = [
    r"discussion",
]

BACK_MATTER_HEADINGS = [
    r"methods",
    r"materials\s+and\s+methods",
    r"materials\s*&\s*methods",
    r"methodology",
    r"experimental\s+procedures",
    r"experimental\s+section",
    r"star\+methods",
    r"online\s+methods",
    r"online\s+content",
    r"references",
    r"bibliography",
    r"data\s+availability",
    r"code\s+availability",
    r"acknowledg(?:e)?ments",
    r"author\s+contributions",
    r"competing\s+interests",
    r"declaration\s+of\s+interests",
    r"ethics\s+declarations",
    r"additional\s+information",
    r"supplementary\s+information",
    r"supplemental\s+information",
    r"extended\s+data",
]

NATURE_BOILERPLATE = {
    "article",
    "letter",
    "brief communication",
    "analysis",
    "resource",
    "technical report",
    "open access",
    "check for updates",
}

# Common publisher/page furniture that should not become paragraphs.
RUNNING_NOISE_EXACT = {
    "article",
    "open",
    "check for updates",
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_pdf_text(text):
    """Clean common PDF artefacts but preserve scientific notation."""

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "\u00ad": "",       # soft hyphen
        "\u200b": "",       # zero-width space
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "\ufffe": "",
        "\uffff": "",
        "\ufffd": "",       # replacement symbol
        "\xa0": " ",        # non-breaking space
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Literal backslashes introduced by some extraction pipelines.
    text = text.replace("\\", "")

    # Remove Unicode control/private-use/surrogate characters, but preserve
    # newlines/tabs for the line-wrap repair below.
    cleaned_chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("C") and ch not in "\n\t":
            continue
        cleaned_chars.append(ch)
    text = "".join(cleaned_chars)

    # Repair line-end word splitting:
    #   transcrip-\n tion -> transcription
    text = re.sub(
        r"([A-Za-z])-[ \t]*\n[ \t]*([a-z])",
        r"\1\2",
        text,
    )

    # Remaining line breaks inside a block become spaces.
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text)
    text = re.sub(r"[ \t]+", " ", text)

    # Punctuation spacing.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    return text.strip()


# ============================================================
# HEADING HELPERS
# ============================================================

def normalize_heading(text):
    text = clean_pdf_text(text).strip()
    return re.sub(r"[:.]\s*$", "", text)


def exact_heading_match(text, patterns):
    text = normalize_heading(text)
    return any(re.fullmatch(p, text, flags=re.IGNORECASE) for p in patterns)


def is_results_heading(text):
    return exact_heading_match(text, RESULTS_HEADINGS)


def is_discussion_heading(text):
    return exact_heading_match(text, DISCUSSION_HEADINGS)


def is_back_matter_heading(text):
    return exact_heading_match(text, BACK_MATTER_HEADINGS)


def is_nature_boilerplate(text):
    return normalize_heading(text).lower() in NATURE_BOILERPLATE


# ============================================================
# NOISE FILTERS
# ============================================================

def is_single_character_noise(text):
    """
    Remove isolated panel labels / axis ticks such as:
        A
        B
        1
        +
        A B C D
        0 1 2 3

    Does not remove ordinary short scientific tokens such as WT or pH.
    """

    text = clean_pdf_text(text)
    if not text:
        return True

    compact = re.sub(r"\s+", "", text)
    alnum = re.sub(r"[^A-Za-z0-9]", "", compact)

    if len(alnum) <= 1:
        return True

    tokens = text.split()

    # A B C D / 0 1 2 / + - style blocks.
    if (
        len(tokens) <= 12
        and all(re.fullmatch(r"[A-Za-z0-9]|[+\-]", t) for t in tokens)
    ):
        return True

    # Pure short numeric axis-label blocks.
    if (
        len(text) <= 40
        and re.fullmatch(r"[\d\s.,+\-]+", text)
    ):
        return True

    return False


def is_running_header_footer(block, page_height):
    """Remove obvious publisher headers/footers without touching body prose."""

    text = normalize_heading(block["clean_text"])
    low = text.lower()
    y0 = block["bbox"][1]
    y1 = block["bbox"][3]

    # Exact small furniture anywhere.
    if low in RUNNING_NOISE_EXACT and len(text) <= 30:
        return True

    # Header/footer zones only.
    in_top = y0 <= page_height * 0.075
    in_bottom = y1 >= page_height * 0.94

    if not (in_top or in_bottom):
        return False

    # Common journal/footer patterns.
    if re.fullmatch(r"\d+", text):
        return True

    if re.search(
        r"\b(nature|cell|scientific reports|www\.nature\.com|doi\.org)\b",
        low,
    ) and len(text) < 180:
        return True

    if re.search(r"\bvol\.?\s*[:.(]", low) and len(text) < 180:
        return True

    return False


def keep_output_text(text):
    """Final safety filter applied before JSON/TXT paragraph output."""
    text = clean_pdf_text(text)
    if not text:
        return False
    if is_single_character_noise(text):
        return False
    return True


# ============================================================
# LINE / BLOCK EXTRACTION
# ============================================================

def canonical_font_root(font_name):
    """
    Collapse regular/bold/italic variants into a common font-family root.

    Examples
    --------
    HardingText-Regular -> hardingtext
    HardingText-Bold    -> hardingtext
    HelveticaNeueLTStd-Roman -> helveticaneueltstd

    PDF font names are not standardized, so this is deliberately conservative.
    """
    name = (font_name or "").strip().lower()
    name = re.sub(r"^\w{6}\+", "", name)  # embedded subset prefix, e.g. ABCDEF+Font
    name = re.sub(
        r"[-_, ]?(regularitalic|bolditalic|semibolditalic|regular|roman|bold|"
        r"italic|oblique|semibold|semi-bold|demi|medium|light|book|it)$",
        "",
        name,
        flags=re.IGNORECASE,
    )
    return name or (font_name or "").strip().lower()


def _line_record(line):
    parts = []
    sizes = []
    bold = 0
    total = 0
    font_chars = Counter()

    for span in line.get("spans", []):
        txt = span.get("text", "")
        if not txt.strip():
            continue

        parts.append(txt)

        size = span.get("size", 0) or 0
        if size:
            sizes.append(size)

        font_name = span.get("font", "")
        root = canonical_font_root(font_name)
        font_chars[root] += max(1, len(txt.strip()))

        font = font_name.lower()
        flags = span.get("flags", 0)

        # Font-name detection plus PyMuPDF's bold flag when available.
        is_bold = (
            "bold" in font
            or "semibold" in font
            or "demi" in font
            or font.endswith("-h")  # common Elsevier/Cell bold font naming
            or bool(flags & (1 << 4))
        )

        if is_bold:
            bold += 1
        total += 1

    raw = " ".join(parts).strip()

    return {
        "raw_text": raw,
        "clean_text": clean_pdf_text(raw),
        "font_size": max(sizes) if sizes else 0,
        "mean_font_size": (sum(sizes) / len(sizes)) if sizes else 0,
        "bold_fraction": (bold / total) if total else 0,
        "font_chars": font_chars,
    }


def _dict_to_blocks(page_dict, page_number):
    blocks = []

    for block_no, block in enumerate(page_dict.get("blocks", [])):
        if "lines" not in block:
            continue

        lines = []
        all_sizes = []
        weighted_bold = 0
        weighted_total = 0
        block_font_chars = Counter()

        for line in block.get("lines", []):
            rec = _line_record(line)
            if not rec["raw_text"]:
                continue

            lines.append(rec)
            if rec["font_size"]:
                all_sizes.append(rec["font_size"])

            # Approximate weighting by one unit per extracted line.
            weighted_bold += rec["bold_fraction"]
            weighted_total += 1
            block_font_chars.update(rec.get("font_chars", {}))

        if not lines:
            continue

        raw_text = "\n".join(x["raw_text"] for x in lines).strip()
        clean_text = clean_pdf_text(raw_text)

        if not clean_text:
            continue

        bbox = tuple(block.get("bbox", (0, 0, 0, 0)))

        blocks.append({
            "page": page_number,
            "block_no": block_no,
            "raw_text": raw_text,
            "clean_text": clean_text,
            "first_line": lines[0]["clean_text"],
            "lines": lines,
            "font_size": max(all_sizes) if all_sizes else 0,
            "mean_font_size": (
                sum(x["mean_font_size"] for x in lines) / len(lines)
                if lines else 0
            ),
            "bold_fraction": (
                weighted_bold / weighted_total if weighted_total else 0
            ),
            "font_chars": block_font_chars,
            "bbox": bbox,
        })

    return blocks


# ============================================================
# COLUMN DETECTION
# ============================================================

def detect_column_count(page, native_blocks):
    """
    Estimate whether a page is single-, double-, or triple-column.

    We only use substantial, non-wide text blocks so figure labels and tiny
    annotations do not create false columns.
    """

    width = page.rect.width
    height = page.rect.height

    candidates = []

    for b in native_blocks:
        x0, y0, x1, y1 = b["bbox"]
        bw = x1 - x0
        text = b["clean_text"]

        if is_running_header_footer(b, height):
            continue
        if is_single_character_noise(text):
            continue

        # Ignore wide title/caption blocks and very tiny blocks.
        if bw > width * 0.62:
            continue
        if len(text) < 80:
            continue

        candidates.append(b)

    if len(candidates) < 2:
        return 1

    # Cluster by left x-position. Indentation within a column is tolerated.
    clusters = []
    tolerance = width * 0.10

    for b in sorted(candidates, key=lambda z: z["bbox"][0]):
        x0 = b["bbox"][0]
        placed = False

        for cluster in clusters:
            center = median(x["bbox"][0] for x in cluster)
            if abs(x0 - center) <= tolerance:
                cluster.append(b)
                placed = True
                break

        if not placed:
            clusters.append([b])

    # Require at least one substantive block in each cluster and collapse
    # clusters whose medians are too close to represent distinct columns.
    medians = sorted(median(x["bbox"][0] for x in c) for c in clusters)

    distinct = []
    min_sep = width * 0.22
    for m in medians:
        if not distinct or abs(m - distinct[-1]) >= min_sep:
            distinct.append(m)

    if len(distinct) >= 3:
        return 3
    if len(distinct) >= 2:
        return 2
    return 1


# ============================================================
# MIXED HEADING+BODY BLOCK SPLITTING
# ============================================================

def split_mixed_heading_block(block):
    """
    Some publisher PDFs put:
        Bold subsection heading
        Normal first paragraph sentence
    in one PyMuPDF text block.

    Split it when the beginning consists of 1-3 bold lines followed by
    non-bold body text.
    """

    lines = block.get("lines", [])
    if len(lines) < 2:
        return [block]

    heading_lines = []
    body_start = None

    for i, line in enumerate(lines[:4]):
        txt = line["clean_text"].strip()
        if not txt:
            continue

        looks_bold = line["bold_fraction"] >= 0.75
        short_enough = len(txt) <= 120

        if looks_bold and short_enough and body_start is None:
            heading_lines.append(line)
            continue

        body_start = i
        break

    if not heading_lines or body_start is None:
        return [block]

    heading_text = clean_pdf_text("\n".join(x["raw_text"] for x in heading_lines))
    body_lines = lines[body_start:]
    body_text = clean_pdf_text("\n".join(x["raw_text"] for x in body_lines))

    # Do not split if the candidate heading is implausibly long.
    if len(heading_text) > 180 or len(heading_text.split()) > 22:
        return [block]

    x0, y0, x1, y1 = block["bbox"]

    heading_block = dict(block)
    heading_block.update({
        "raw_text": "\n".join(x["raw_text"] for x in heading_lines),
        "clean_text": heading_text,
        "first_line": heading_lines[0]["clean_text"],
        "lines": heading_lines,
        "font_size": max((x["font_size"] for x in heading_lines), default=0),
        "mean_font_size": (
            sum(x["mean_font_size"] for x in heading_lines) / len(heading_lines)
            if heading_lines else 0
        ),
        "bold_fraction": (
            sum(x["bold_fraction"] for x in heading_lines) / len(heading_lines)
            if heading_lines else 0
        ),
        "font_chars": sum((x.get("font_chars", Counter()) for x in heading_lines), Counter()),
        "synthetic_split": "heading",
    })

    body_block = dict(block)
    body_block.update({
        "raw_text": "\n".join(x["raw_text"] for x in body_lines),
        "clean_text": body_text,
        "first_line": body_lines[0]["clean_text"] if body_lines else "",
        "lines": body_lines,
        "font_size": max((x["font_size"] for x in body_lines), default=0),
        "mean_font_size": (
            sum(x["mean_font_size"] for x in body_lines) / len(body_lines)
            if body_lines else 0
        ),
        "bold_fraction": (
            sum(x["bold_fraction"] for x in body_lines) / len(body_lines)
            if body_lines else 0
        ),
        "font_chars": sum((x.get("font_chars", Counter()) for x in body_lines), Counter()),
        "synthetic_split": "body",
    })

    return [heading_block, body_block]


# ============================================================
# PDF EXTRACTION WITH LAYOUT-AWARE ORDER
# ============================================================

def extract_blocks(pdf_file):
    """
    Extract blocks page-by-page.

    Critical change from the previous version:
        - multi-column page -> sort=False (native PDF reading order)
        - single-column page -> sort=True (coordinate order)

    This avoids the classic PyMuPDF double-column failure where a lower block
    from the left column is sorted after a RESULTS heading in the right column.
    """

    doc = fitz.open(pdf_file)
    output = []

    for page_number, page in enumerate(doc, start=1):
        # First inspect native order to detect the layout.
        native_dict = page.get_text("dict", sort=False)
        native_blocks = _dict_to_blocks(native_dict, page_number)

        n_columns = detect_column_count(page, native_blocks)

        if n_columns >= 2:
            page_blocks = native_blocks
            order_mode = f"native_{n_columns}_column"
        else:
            sorted_dict = page.get_text("dict", sort=True)
            page_blocks = _dict_to_blocks(sorted_dict, page_number)
            order_mode = "sorted_single_column"

        # Remove obvious headers/footers and tiny figure-panel fragments.
        cleaned_page_blocks = []
        for b in page_blocks:
            if is_running_header_footer(b, page.rect.height):
                continue
            if is_single_character_noise(b["clean_text"]):
                continue

            b["column_count"] = n_columns
            b["reading_order_mode"] = order_mode

            # Split heading+body blocks when possible.
            for piece in split_mixed_heading_block(b):
                if keep_output_text(piece["clean_text"]):
                    cleaned_page_blocks.append(piece)

        output.extend(cleaned_page_blocks)

    doc.close()
    return output


# ============================================================
# BODY FONT / HEADING DETECTION
# ============================================================

def estimate_body_font_size(blocks):
    """
    Estimate prose font size while excluding figure/table captions and tiny
    graphic labels. Using selected Results blocks gives especially reliable
    estimates for multi-column publisher PDFs.
    """
    sizes = []
    for b in blocks:
        text = b["clean_text"]
        if len(text) < 120 or b["mean_font_size"] <= 0:
            continue
        if re.match(
            r"^(fig(?:ure)?|table|extended data|supplementary|supplemental)",
            text,
            flags=re.IGNORECASE,
        ):
            continue
        sizes.append(b["mean_font_size"])

    return median(sizes) if sizes else 10.0


def looks_like_sentence(text):
    text = text.strip()
    if not text:
        return False
    if text.endswith((".", "?", "!", ";")):
        return True
    return len(text.split()) > 18


def title_like_heading(text):
    text = normalize_heading(text)
    words = text.split()

    if not words:
        return False
    if len(words) > 18 or len(text) > 180:
        return False
    if looks_like_sentence(text):
        return False
    if re.fullmatch(r"[\d\s.,()\-]+", text):
        return False
    if re.match(
        r"^(fig(?:ure)?|table|extended data|supplementary|supplemental)",
        text,
        flags=re.IGNORECASE,
    ):
        return False

    return True


def is_heading_like(block, body_font_size):
    text = block["clean_text"].strip()
    first_line = block["first_line"].strip()

    if not text:
        return False

    for candidate in (text, first_line):
        if (
            is_results_heading(candidate)
            or is_discussion_heading(candidate)
            or is_back_matter_heading(candidate)
        ):
            return True

    if len(text.split()) > 22 or len(text) > 200:
        return False
    if text.endswith((".", ";", ",")):
        return False

    larger_font = block["font_size"] >= body_font_size * 1.08
    mostly_bold = block["bold_fraction"] >= 0.70
    title_like = title_like_heading(text)

    # A synthetic heading split is intentionally high-confidence.
    synthetic = block.get("synthetic_split") == "heading"
    synthetic_body = block.get("synthetic_split") == "body"

    # A body fragment split away from a bold heading must not be promoted
    # back into a heading by generic heuristics.
    if synthetic_body:
        return False

    # Avoid treating a body sentence fragment as a heading merely because
    # it is short and lacks terminal punctuation. Linguistic title-likeness
    # only supports a heading when there is also some typographic evidence.
    typographic_support = larger_font or block["bold_fraction"] >= 0.30

    return synthetic or larger_font or mostly_bold or (title_like and typographic_support)


# ============================================================
# NATURE DETECTION
# ============================================================

def looks_like_nature_paper(blocks):
    text = " ".join(
        b["clean_text"] for b in blocks if b["page"] <= 2
    ).lower()

    indicators = [
        "nature communications",
        "nature plants",
        "nature genetics",
        "nature biotechnology",
        "nature methods",
        "nature metabolism",
        "nature ecology",
        "nature medicine",
        "www.nature.com",
        "springer nature",
        "s41467-",
        "s41586-",
        "s41587-",
        "s41588-",
        "s41589-",
    ]

    return any(x in text for x in indicators)


def is_substantive_prose(block):
    text = block["clean_text"].strip()
    if len(text) < 100:
        return False
    if is_nature_boilerplate(text):
        return False
    if re.match(
        r"^(received|accepted|published|https?://|doi)",
        text,
        flags=re.IGNORECASE,
    ):
        return False
    return True


# ============================================================
# SECTION BOUNDARY DETECTION
# ============================================================

def find_explicit_results_heading(blocks):
    for i, block in enumerate(blocks):
        for candidate in (block["clean_text"], block["first_line"]):
            if is_results_heading(candidate):
                return i, normalize_heading(candidate)
    return None, None


def find_discussion_after(blocks, start_index):
    for i in range(start_index + 1, len(blocks)):
        for candidate in (blocks[i]["clean_text"], blocks[i]["first_line"]):
            if is_discussion_heading(candidate):
                return i
    return None


def find_back_matter_after(blocks, start_index):
    for i in range(start_index + 1, len(blocks)):
        for candidate in (blocks[i]["clean_text"], blocks[i]["first_line"]):
            if is_back_matter_heading(candidate):
                return i
    return None


def find_first_nature_body_heading(blocks, body_font_size, min_intro_paragraphs=2):
    """Scan forward from the beginning and choose the first real body heading."""

    prose_seen = 0

    for i, block in enumerate(blocks):
        text = block["clean_text"].strip()

        if not text:
            continue
        if is_nature_boilerplate(text):
            continue
        if is_discussion_heading(text) or is_back_matter_heading(text):
            continue

        if not is_heading_like(block, body_font_size):
            if is_substantive_prose(block):
                prose_seen += 1
            continue

        if prose_seen >= min_intro_paragraphs:
            return i

    return None


def find_section_boundaries(blocks, nature_fallback=True):
    body_font_size = estimate_body_font_size(blocks)

    # 1. Conventional explicit Results.
    result_index, result_heading = find_explicit_results_heading(blocks)

    if result_index is not None:
        combined = bool(
            re.fullmatch(
                r"results\s+and\s+discussions?",
                result_heading,
                flags=re.IGNORECASE,
            )
        )

        if not combined:
            discussion_index = find_discussion_after(blocks, result_index)
            if discussion_index is not None:
                return {
                    "mode": "explicit_results",
                    "start_index": result_index + 1,
                    "end_index": discussion_index,
                    "start_heading": result_heading,
                    "end_heading": blocks[discussion_index]["clean_text"],
                }

        # Results & Discussion, or Results with no Discussion.
        back_index = find_back_matter_after(blocks, result_index)
        return {
            "mode": "explicit_results_and_discussion" if combined else "explicit_results_no_discussion",
            "start_index": result_index + 1,
            "end_index": back_index if back_index is not None else len(blocks),
            "start_heading": result_heading,
            "end_heading": (
                blocks[back_index]["clean_text"] if back_index is not None else None
            ),
        }

    # 2. Nature-style fallback without Results heading.
    if nature_fallback and looks_like_nature_paper(blocks):
        first_heading = find_first_nature_body_heading(blocks, body_font_size)
        if first_heading is None:
            raise RuntimeError(
                "Nature-style article detected, but no first body subsection heading could be identified."
            )

        discussion_index = find_discussion_after(blocks, first_heading)
        if discussion_index is not None:
            return {
                "mode": "nature_first_heading_to_discussion",
                "start_index": first_heading,
                "end_index": discussion_index,
                "start_heading": blocks[first_heading]["clean_text"],
                "end_heading": blocks[discussion_index]["clean_text"],
            }

        back_index = find_back_matter_after(blocks, first_heading)
        return {
            "mode": "nature_first_heading_to_end",
            "start_index": first_heading,
            "end_index": back_index if back_index is not None else len(blocks),
            "start_heading": blocks[first_heading]["clean_text"],
            "end_heading": (
                blocks[back_index]["clean_text"] if back_index is not None else None
            ),
        }

    return None


def is_short_graphic_fragment(block, body_font_size):
    """Remove short text fragments coming from plots, diagrams, and panel labels."""
    text = block["clean_text"].strip()
    if not text:
        return True

    low = text.lower()
    if "legend continued on next page" in low:
        return True

    if block.get("synthetic_split") == "heading":
        return False

    if is_results_heading(text) or is_discussion_heading(text) or is_back_matter_heading(text):
        return False

    words = text.split()
    if len(text) > 80 or len(words) > 10:
        return False

    # Short numeric/axis fragments such as "Z-score -2 0 3" or "12 24 48".
    numeric_tokens = sum(bool(re.fullmatch(r"[+\-]?\d+(?:\.\d+)?", w.strip("(),:%"))) for w in words)
    if numeric_tokens >= 2 and not text.endswith((".", "?", "!")):
        return True

    # Very short labels that are smaller than normal prose are almost always
    # figure annotations, even when bold (e.g. "Heinz Chr 12:").
    if len(text) <= 55 and block["font_size"] < body_font_size * 0.95:
        return True

    # Non-bold short labels near body size (gene names, axis labels, etc.).
    if (
        len(text) <= 70
        and len(words) <= 8
        and block["bold_fraction"] < 0.60
        and block["font_size"] <= body_font_size * 1.10
        and not text.endswith((".", "?", "!"))
    ):
        return True

    return False



# ============================================================
# FIGURE / DIAGRAM TEXT FILTERING
# ============================================================

CAPTION_PREFIX_RE = re.compile(
    r"^(?:"
    r"fig(?:ure)?\.?\s*(?:s\s*)?\d+[a-z]?"
    r"|table\s*(?:s\s*)?\d+[a-z]?"
    r"|extended\s+data\s+fig(?:ure)?\.?\s*\d+[a-z]?"
    r"|supplementary\s+fig(?:ure)?\.?\s*(?:s\s*)?\d+[a-z]?"
    r"|supplemental\s+fig(?:ure)?\.?\s*(?:s\s*)?\d+[a-z]?"
    r")",
    flags=re.IGNORECASE,
)


def is_figure_or_table_caption(text):
    """Return True for figure/table caption or legend blocks."""
    text = clean_pdf_text(text).strip()
    if not text:
        return False

    # Standard caption starts: Fig. 2, Figure 3, Figure S2, Table S1, etc.
    if CAPTION_PREFIX_RE.match(text):
        return True

    # Publisher-specific continuation markers.
    low = text.lower()
    if "legend continued on next page" in low:
        return True
    if re.match(r"^\(legend continued", low):
        return True

    return False


def is_caption_continuation(block, body_font_size):
    """
    Detect caption/legend fragments that continue in a separate PDF text block.

    Common examples are:
        (C) Falcarindiol production in WT ...
        (D) Number of bacteria ...
        See also Figure S6 and Table S4.

    These often do not begin with the word Figure/Table, especially when a
    multi-panel legend continues onto the next page. They are usually rendered
    smaller than manuscript prose.
    """
    text = clean_pdf_text(block.get("clean_text", "")).strip()
    if not text:
        return False

    mean_size = block.get("mean_font_size", 0) or 0
    small_caption_font = (
        body_font_size > 0
        and mean_size > 0
        and mean_size <= body_font_size * 0.90
    )

    # Multi-panel legend continuation: (A), (B), (C), ...
    if (
        small_caption_font
        and re.match(r"^\([A-Z]\)\s+", text)
        and len(text) >= 60
    ):
        return True

    # Typical tail of a figure/table legend.
    if (
        small_caption_font
        and re.match(
            r"^(see\s+also|error\s+bars|data\s+are|values\s+are|"
            r"bars\s+represent|dots\s+represent|n\s*=)",
            text,
            flags=re.IGNORECASE,
        )
    ):
        return True

    return False


def estimate_body_font_profile(blocks):
    """
    Learn the main prose font family/families from the selected scientific body.

    Why this helps
    --------------
    Text embedded inside figures is frequently still real PDF text, so PyMuPDF
    extracts it. In publisher PDFs, however, figure/diagram text very often uses
    a different font family and a smaller font size than manuscript prose.

    We therefore estimate:
      - normal body font size
      - font-family roots used for body prose

    Captions are excluded from the training sample.
    """
    body_size = estimate_body_font_size(blocks)

    counts = Counter()

    # First pass: long prose close to the estimated body size.
    for block in blocks:
        text = block["clean_text"].strip()

        if len(text) < 120:
            continue
        if is_figure_or_table_caption(text):
            continue
        if block.get("synthetic_split") == "heading":
            continue

        mean_size = block.get("mean_font_size", 0) or 0
        if mean_size <= 0:
            continue

        # Body prose tends to cluster tightly around its normal font size.
        if not (body_size * 0.88 <= mean_size <= body_size * 1.12):
            continue

        counts.update(block.get("font_chars", {}))

    # Fallback if a very unusual PDF prevented the first pass from learning.
    if not counts:
        for block in blocks:
            text = block["clean_text"].strip()
            if len(text) >= 120 and not is_figure_or_table_caption(text):
                counts.update(block.get("font_chars", {}))

    if not counts:
        return {
            "body_font_size": body_size,
            "body_font_roots": set(),
            "font_counts": {},
        }

    total = sum(counts.values())
    selected = set()
    running = 0

    # Keep the dominant prose families accounting for up to 90% of characters.
    # A minimum 5% share prevents many tiny embedded fonts from being learned.
    for root, n_chars in counts.most_common():
        share = n_chars / total
        if share < 0.05 and selected:
            break

        selected.add(root)
        running += n_chars

        if running / total >= 0.90:
            break

    return {
        "body_font_size": body_size,
        "body_font_roots": selected,
        "font_counts": dict(counts),
    }


def body_font_fraction(block, body_font_roots):
    """Fraction of block characters rendered using learned prose fonts."""
    font_chars = block.get("font_chars", {})
    total = sum(font_chars.values())

    if total <= 0 or not body_font_roots:
        return None

    body_chars = sum(
        n for root, n in font_chars.items()
        if root in body_font_roots
    )

    return body_chars / total


def is_likely_figure_text(block, font_profile):
    """
    Detect words/numbers embedded *inside* plots, diagrams and figure panels.

    Figure/table captions are handled separately and removed before this function
    is called.

    Signals are combined rather than relying on one brittle keyword rule:
      1. text substantially smaller than manuscript prose;
      2. font family unrelated to the learned prose font;
      3. graphic-like numeric/token structure.

    Section headings are protected when they are clearly larger/bolder than
    prose. This is important for Nature papers.
    """
    text = block["clean_text"].strip()

    if not text:
        return True

    if is_figure_or_table_caption(text):
        return True

    if (
        is_results_heading(text)
        or is_discussion_heading(text)
        or is_back_matter_heading(text)
    ):
        return False

    # Explicit subsection heading separated by split_mixed_heading_block().
    if block.get("synthetic_split") == "heading":
        return False

    body_size = font_profile.get("body_font_size", 0) or 0
    body_roots = font_profile.get("body_font_roots", set())

    if body_size <= 0:
        return False

    mean_size = block.get("mean_font_size", 0) or 0
    max_size = block.get("font_size", 0) or 0
    frac = body_font_fraction(block, body_roots)

    # Protect clear typographic section headings.
    if (
        max_size >= body_size * 1.08
        and block.get("bold_fraction", 0) >= 0.35
        and len(text) <= 220
    ):
        return False

    # Strong signal #1:
    # very small text relative to manuscript prose.
    # Nature figure text in the example is 6 pt versus ~8.25 pt body text.
    if mean_size > 0 and mean_size <= body_size * 0.80:
        return True

    # Strong signal #2:
    # non-body font + smaller-than-body text.
    # This catches text such as Helvetica inside Nature figures while body
    # prose uses HardingText.
    if (
        frac is not None
        and frac < 0.15
        and mean_size > 0
        and mean_size <= body_size * 0.95
    ):
        return True

    # Strong signal #3:
    # mostly non-body font, fairly short, and not normal sentence prose.
    if (
        frac is not None
        and frac < 0.10
        and len(text) <= 300
        and mean_size > 0
        and mean_size < body_size
        and not text.rstrip().endswith((".", "?", "!"))
    ):
        return True

    # Graphic / axis / tick strings.
    tokens = text.split()
    numeric_tokens = sum(
        bool(re.fullmatch(r"[+\-−]?\d+(?:[.,]\d+)?(?:%|×)?", tok.strip("()[],:;")))
        for tok in tokens
    )

    if (
        len(tokens) <= 20
        and numeric_tokens >= max(3, len(tokens) // 2)
        and mean_size > 0
        and mean_size < body_size * 0.95
    ):
        return True

    return False


def _starts_with_lowercase(text):
    m = re.search(r"[A-Za-z]", text)
    return bool(m and m.group(0).islower())


def merge_continuation_paragraphs(items):
    """
    Merge body fragments split by column/page boundaries when the previous
    fragment has no sentence-ending punctuation and the next begins lowercase.
    """
    merged = []
    for item in items:
        if not merged:
            merged.append(item)
            continue

        prev = merged[-1]
        can_merge = (
            not prev["heading"]
            and not item["heading"]
            and prev.get("section_heading") == item.get("section_heading")
            and not prev["text"].rstrip().endswith((".", "?", "!", ";", ":"))
            and _starts_with_lowercase(item["text"])
        )

        if can_merge:
            prev["text"] = clean_pdf_text(prev["text"] + " " + item["text"])
            prev["raw_text"] = prev["raw_text"].rstrip() + "\n" + item["raw_text"].lstrip()
            prev["page_end"] = item["page_end"]
        else:
            merged.append(item)

    return merged


# ============================================================
# BLOCKS -> OUTPUT PARAGRAPHS
# ============================================================

def blocks_to_paragraphs(
    section_blocks,
    body_font_size,
    font_profile=None,
    filter_figure_text=True,
    remove_captions=True,
):
    paragraphs = []
    current_subsection = None

    for block in section_blocks:
        text = block["clean_text"].strip()

        if not keep_output_text(text):
            continue

        # Remove figure/table captions and legends entirely, including
        # continuation fragments that begin with panel labels such as (C)/(D).
        if remove_captions and (
            is_figure_or_table_caption(text)
            or is_caption_continuation(block, body_font_size)
        ):
            continue

        if is_short_graphic_fragment(block, body_font_size):
            continue
        if (
            filter_figure_text
            and font_profile is not None
            and is_likely_figure_text(block, font_profile)
        ):
            continue

        # Caption blocks have already been removed above.
        heading = is_heading_like(block, body_font_size)

        if heading:
            current_subsection = text

        item = {
            "page_start": block["page"],
            "page_end": block["page"],
            "heading": bool(heading),
            "section_heading": text if heading else current_subsection,
            "text": text,
            "raw_text": block["raw_text"],
        }

        paragraphs.append(item)

    return merge_continuation_paragraphs(paragraphs)


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_results_paragraphs(
    pdf_file,
    nature_fallback=True,
    filter_figure_text=True,
    remove_captions=True,
    resolve_doi=True,
):
    blocks = extract_blocks(pdf_file)

    if not blocks:
        raise RuntimeError(f"No extractable text found in: {pdf_file}")

    boundaries = find_section_boundaries(
        blocks,
        nature_fallback=nature_fallback,
    )

    if boundaries is None:
        raise RuntimeError(
            "Could not identify a Results section or an appropriate Nature-style body."
        )

    start = boundaries["start_index"]
    end = boundaries["end_index"]
    section_blocks = blocks[start:end]

    # Estimate typography from the selected scientific section rather than
    # from the whole PDF, where small Methods/reference/caption fonts can skew
    # the estimate.
    body_font_size = estimate_body_font_size(section_blocks)
    font_profile = estimate_body_font_profile(section_blocks)
    paragraphs = blocks_to_paragraphs(
        section_blocks,
        body_font_size,
        font_profile=font_profile,
        filter_figure_text=filter_figure_text,
        remove_captions=remove_captions,
    )

    pages = [p["page_start"] for p in paragraphs] if paragraphs else []

    output_doi = resolve_doi_from_hashed_pdf(pdf_file) if resolve_doi else None

    return {
        "source_document": Path(pdf_file).name,
        "output_doi": output_doi,
        "extraction_mode": boundaries["mode"],
        "start_heading": boundaries["start_heading"],
        "end_heading": boundaries["end_heading"],
        "start_pdf_page": min(pages) if pages else None,
        "end_pdf_page": max(pages) if pages else None,
        "paragraphs": paragraphs,
    }


# ============================================================
# EXPORT
# ============================================================

def save_clean_text(result, output_file):
    with open(output_file, "w", encoding="utf-8") as handle:
        current_page = None

        for item in result["paragraphs"]:
            page = item["page_start"]

            if page != current_page:
                handle.write(f"\n\n===== PDF PAGE {page} =====\n\n")
                current_page = page

            if item["heading"]:
                handle.write(f"\n### {item['text']}\n\n")
            else:
                handle.write(item["text"] + "\n\n")


def save_json(result, output_file):
    with open(output_file, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)


def print_preview(result):
    print("\n" + "=" * 72)
    print("SOURCE:", result["source_document"])
    print("DOI:", result.get("output_doi"))
    print("MODE:", result["extraction_mode"])
    print("START:", result["start_heading"])
    print("END:", result["end_heading"])
    print("PDF PAGES:", result["start_pdf_page"], "->", result["end_pdf_page"])
    print("PARAGRAPHS:", len(result["paragraphs"]))
    print("=" * 72)

    for item in result["paragraphs"]:
        if item["heading"]:
            print(f"\n\n### {item['text']}")
        else:
            print(f"\n[PDF page {item['page_start']}] {item['text']}")


# ============================================================
# BATCH / PARALLEL PROCESSING
# ============================================================

def detect_available_cores():
    """Return the number of logical CPU cores visible to Python."""
    return os.cpu_count() or 1


def collect_pdf_files(input_path, recursive=False):
    """
    Accept either a single PDF or a directory.

    Directory mode scans for *.pdf files. Use --recursive to include
    subdirectories. Matching is case-insensitive for the extension.
    """
    input_path = Path(input_path).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {input_path}")
        return [input_path], input_path.parent

    if not input_path.is_dir():
        raise ValueError(f"Input path is neither a PDF nor a directory: {input_path}")

    iterator = input_path.rglob("*") if recursive else input_path.glob("*")
    pdfs = sorted(
        p.resolve()
        for p in iterator
        if p.is_file() and p.suffix.lower() == ".pdf"
    )

    if not pdfs:
        scope = "recursively" if recursive else "in the folder"
        raise RuntimeError(f"No PDF files found {scope}: {input_path}")

    return pdfs, input_path


def _safe_relative_parent(pdf_path, input_root):
    """
    Preserve subdirectory structure in recursive folder mode so PDFs with the
    same basename do not overwrite one another.
    """
    try:
        rel = pdf_path.relative_to(input_root)
        return rel.parent
    except ValueError:
        return Path()


def process_one_pdf_job(job):
    """
    Top-level worker function for ProcessPoolExecutor.

    Each process opens its own PDF independently, which is safer than sharing
    PyMuPDF document objects between workers.
    """
    pdf_path = Path(job["pdf_path"])
    outdir = Path(job["outdir"])

    try:
        outdir.mkdir(parents=True, exist_ok=True)

        result = extract_results_paragraphs(
            pdf_path,
            nature_fallback=job["nature_fallback"],
            filter_figure_text=job["filter_figure_text"],
            remove_captions=job["remove_captions"],
            resolve_doi=job.get("resolve_doi", True),
        )

        json_file = outdir / f"{pdf_path.stem}_results.json"
        txt_file = outdir / f"{pdf_path.stem}_results.txt"

        save_json(result, json_file)
        save_clean_text(result, txt_file)

        return {
            "status": "ok",
            "source_document": str(pdf_path),
            "json_file": str(json_file),
            "txt_file": str(txt_file),
            "output_doi": result.get("output_doi"),
            "extraction_mode": result.get("extraction_mode"),
            "start_heading": result.get("start_heading"),
            "end_heading": result.get("end_heading"),
            "start_pdf_page": result.get("start_pdf_page"),
            "end_pdf_page": result.get("end_pdf_page"),
            "paragraph_count": len(result.get("paragraphs", [])),
        }

    except Exception as exc:
        return {
            "status": "error",
            "source_document": str(pdf_path),
            "error": f"{type(exc).__name__}: {exc}",
        }


def run_batch(
    pdf_files,
    input_root,
    outdir,
    workers,
    nature_fallback=True,
    filter_figure_text=True,
    remove_captions=True,
    resolve_doi=True,
):
    """Process multiple PDFs concurrently using separate worker processes."""

    outdir = Path(outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    jobs = []
    for pdf_path in pdf_files:
        relative_parent = _safe_relative_parent(pdf_path, input_root)
        pdf_outdir = outdir / relative_parent

        jobs.append({
            "pdf_path": str(pdf_path),
            "outdir": str(pdf_outdir),
            "nature_fallback": nature_fallback,
            "filter_figure_text": filter_figure_text,
            "remove_captions": remove_captions,
            "resolve_doi": resolve_doi,
        })

    results = []
    total = len(jobs)

    # A single worker avoids multiprocessing startup overhead and is useful for
    # debugging, while still using exactly the same code path.
    if workers == 1:
        for i, job in enumerate(jobs, start=1):
            res = process_one_pdf_job(job)
            results.append(res)
            if res["status"] == "ok":
                print(
                    f"[{i}/{total}] OK     {Path(res['source_document']).name} "
                    f"({res['paragraph_count']} paragraphs)"
                )
            else:
                print(
                    f"[{i}/{total}] FAILED {Path(res['source_document']).name}: "
                    f"{res['error']}"
                )
        return results

    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_job = {
            executor.submit(process_one_pdf_job, job): job
            for job in jobs
        }

        completed = 0
        for future in as_completed(future_to_job):
            completed += 1
            job = future_to_job[future]

            try:
                res = future.result()
            except Exception as exc:
                # Normally process_one_pdf_job catches per-PDF errors, but this
                # also catches worker-process failures themselves.
                res = {
                    "status": "error",
                    "source_document": job["pdf_path"],
                    "error": f"Worker failure: {type(exc).__name__}: {exc}",
                }

            results.append(res)

            name = Path(res["source_document"]).name
            if res["status"] == "ok":
                print(
                    f"[{completed}/{total}] OK     {name} "
                    f"({res['paragraph_count']} paragraphs)"
                )
            else:
                print(
                    f"[{completed}/{total}] FAILED {name}: {res['error']}"
                )

    # Keep summary deterministic regardless of completion order.
    results.sort(key=lambda x: x["source_document"])
    return results


def save_batch_summary(results, output_file, detected_cores, workers):
    """Write a compact machine-readable batch run report."""
    summary = {
        "detected_logical_cores": detected_cores,
        "workers_used": workers,
        "total_pdfs": len(results),
        "successful": sum(r["status"] == "ok" for r in results),
        "failed": sum(r["status"] != "ok" for r in results),
        "files": results,
    }

    with open(output_file, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract Results or equivalent main scientific body from one PDF "
            "or all PDFs in a folder, with optional parallel processing."
        )
    )

    parser.add_argument(
        "input",
        help="Input PDF file or folder containing PDF files",
    )
    parser.add_argument(
        "--outdir",
        default="extracted_results",
        help="Output directory (default: extracted_results)",
    )
    parser.add_argument(
        "--threads",
        "--cores",
        dest="workers",
        type=int,
        default=None,
        help=(
            "Number of parallel worker processes. --threads and --cores are "
            "aliases. Default: automatically use all detected logical CPU cores."
        ),
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="When input is a folder, also process PDFs in subdirectories.",
    )
    parser.add_argument(
        "--no-nature-fallback",
        action="store_true",
        help="Disable Nature-style fallback when Results heading is absent.",
    )
    parser.add_argument(
        "--keep-figure-text",
        action="store_true",
        help=(
            "Keep text embedded inside figures/diagrams. By default the script "
            "filters likely figure-internal text."
        ),
    )
    parser.add_argument(
        "--keep-captions",
        action="store_true",
        help=(
            "Keep figure/table captions and legends. By default captions/legends "
            "are removed from JSON and TXT output."
        ),
    )
    parser.add_argument(
        "--no-doi-resolution",
        action="store_true",
        help=(
            "Do not resolve DOI URLs from hash-named PDFs. By default the script "
            "extracts DOI candidates from each PDF and keeps the one whose DOI "
            "hash matches the filename hash."
        ),
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help=(
            "For a single PDF, do not print the extracted paragraphs. In folder "
            "mode, only compact per-file progress is printed regardless."
        ),
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    pdf_files, input_root = collect_pdf_files(
        input_path,
        recursive=args.recursive,
    )

    detected_cores = detect_available_cores()

    if args.workers is None:
        workers = detected_cores
    else:
        if args.workers < 1:
            parser.error("--threads/--cores must be an integer >= 1")
        workers = args.workers

    # There is no benefit in launching more workers than PDFs.
    workers = min(workers, len(pdf_files))

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Detected logical CPU cores: {detected_cores}")
    print(f"PDF files to process:       {len(pdf_files)}")
    print(f"Parallel workers used:      {workers}")

    # Preserve the original rich single-file preview behavior.
    if len(pdf_files) == 1 and input_path.is_file():
        pdf_path = pdf_files[0]

        result = extract_results_paragraphs(
            pdf_path,
            nature_fallback=not args.no_nature_fallback,
            filter_figure_text=not args.keep_figure_text,
            remove_captions=not args.keep_captions,
            resolve_doi=not args.no_doi_resolution,
        )

        json_file = outdir / f"{pdf_path.stem}_results.json"
        txt_file = outdir / f"{pdf_path.stem}_results.txt"

        save_json(result, json_file)
        save_clean_text(result, txt_file)

        if not args.no_preview:
            print_preview(result)

        print(f"\nJSON saved to: {json_file}")
        print(f"Clean text saved to: {txt_file}")
        return

    # Folder / multi-PDF mode.
    results = run_batch(
        pdf_files=pdf_files,
        input_root=input_root,
        outdir=outdir,
        workers=workers,
        nature_fallback=not args.no_nature_fallback,
        filter_figure_text=not args.keep_figure_text,
        remove_captions=not args.keep_captions,
        resolve_doi=not args.no_doi_resolution,
    )

    summary_file = outdir / "batch_summary.json"
    save_batch_summary(
        results,
        summary_file,
        detected_cores=detected_cores,
        workers=workers,
    )

    successful = sum(r["status"] == "ok" for r in results)
    failed = len(results) - successful

    print("\n" + "=" * 72)
    print("BATCH COMPLETE")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Summary:    {summary_file}")
    print("=" * 72)

    # Non-zero exit code is useful in shell pipelines if any PDF failed.
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
