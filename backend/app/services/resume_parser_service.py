"""Real PDF resume parsing: text extraction + heuristic section segmentation.

Pure extraction, no LLM hallucination risk — sections are located via regex
and layout heuristics over the actual extracted text.
"""
from __future__ import annotations

import re
from typing import Dict, List

import pdfplumber

from app.schemas.resume import ContactInfo, ParsedResumeData

SECTION_HEADERS = {
    "skills": [r"^skills\b", r"^technical skills\b", r"^core competencies\b"],
    "experience": [r"^experience\b", r"^work experience\b", r"^employment history\b", r"^professional experience\b"],
    "education": [r"^education\b", r"^academic background\b"],
    "projects": [r"^projects\b", r"^personal projects\b"],
    "certifications": [r"^certifications?\b", r"^licenses?\b"],
    "links": [r"^links\b", r"^portfolio\b"],
}

# Headers we recognize but whose content isn't part of ParsedResumeData's
# schema (achievements, summary, etc.) — matching one of these stops
# whatever section was previously active, so e.g. an "Achievements" block
# doesn't silently get appended onto the preceding "Education" section.
IGNORED_SECTION_HEADERS = [
    r"^key achievements\b",
    r"^achievements\b",
    r"^awards\b",
    r"^summary\b",
    r"^objective\b",
    r"^interests\b",
    r"^hobbies\b",
    r"^references\b",
    r"^languages spoken\b",
]

_FULL_WIDTH_GAP_THRESHOLD = 20.0  # points; see _extract_page_text

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
URL_RE = re.compile(r"https?://[^\s,)]+|(?:www\.)[^\s,)]+")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file's bytes using pdfplumber.

    Detects two-column resume layouts (very common) and extracts each
    column separately, top-to-bottom, left column then right column.
    Falling back to pdfplumber's default line-based extraction for a
    two-column page interleaves the columns line-by-line by vertical
    position, producing garbled merged text and breaking section-header
    detection downstream.
    """
    text_parts: List[str] = []
    import io

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(_extract_page_text(page))
    return "\n".join(text_parts)


def _extract_page_text(page) -> str:
    words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
    if not words:
        return page.extract_text() or ""

    gutter = _detect_column_gutter(page, words)
    if gutter is None:
        return page.extract_text() or ""

    # A resume's name/title/contact/summary block usually sits full-width
    # above the two-column body. Splitting those lines by the gutter x would
    # shred them into two disconnected fragments, so identify and preserve
    # them intact: a genuine full-width line has *normal word spacing* where
    # it crosses the gutter (it's one continuous sentence), whereas a line
    # where two unrelated column lines just happen to share the same
    # vertical position has a large gap there (the column gutter itself).
    lines = _group_words_into_lines(words)
    body_start = 0
    for line_words in lines:
        sorted_line = sorted(line_words, key=lambda w: w["x0"])
        left = [w for w in sorted_line if (w["x0"] + w["x1"]) / 2 <= gutter]
        right = [w for w in sorted_line if (w["x0"] + w["x1"]) / 2 > gutter]
        if not left or not right:
            body_start += 1  # one-sided line (e.g. name/title) — safe either way
            continue
        gap = right[0]["x0"] - left[-1]["x1"]
        if gap < _FULL_WIDTH_GAP_THRESHOLD:
            body_start += 1
        else:
            break

    header_lines = [_line_words_to_text(line) for line in lines[:body_start]]

    body_words = [w for line in lines[body_start:] for w in line]
    left_words = [w for w in body_words if (w["x0"] + w["x1"]) / 2 <= gutter]
    right_words = [w for w in body_words if (w["x0"] + w["x1"]) / 2 > gutter]
    left_lines = _words_to_lines(left_words)
    right_lines = _words_to_lines(right_words)

    return "\n".join(header_lines + left_lines + right_lines)


def _detect_column_gutter(page, words: List[dict]) -> float | None:
    """Looks for a vertical band with no word bounding boxes crossing it,
    roughly in the middle third of the page — the visual gutter between two
    columns. Returns the gutter's x-coordinate, or None if the page reads as
    a single column.
    """
    width = page.width
    candidates = [width * (0.35 + 0.01 * i) for i in range(31)]  # 35%..65% of width

    best_x: float | None = None
    best_crossing = None
    for x in candidates:
        crossing = sum(1 for w in words if w["x0"] < x < w["x1"])
        if best_crossing is None or crossing < best_crossing:
            best_crossing = crossing
            best_x = x

    # A page with a full-width header/summary above two-column body content
    # will still have a handful of words straddling the gutter x (the
    # header's long lines), so "must be exactly 0" is too strict — allow a
    # small fraction of words to cross.
    crossing_threshold = max(3, round(0.01 * len(words)))
    if best_crossing is None or best_crossing > crossing_threshold or best_x is None:
        return None

    left_count = sum(1 for w in words if (w["x0"] + w["x1"]) / 2 <= best_x)
    right_count = len(words) - left_count
    min_side = min(left_count, right_count)
    if min_side < max(10, 0.15 * len(words)):
        return None

    return best_x


def _group_words_into_lines(words: List[dict], y_tolerance: float = 3.0) -> List[List[dict]]:
    """Groups words into text lines by vertical position (top-to-bottom,
    each line's words unsorted horizontally — callers sort as needed).
    """
    if not words:
        return []

    lines: List[List[dict]] = []
    current_line: List[dict] = []
    current_top: float | None = None

    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if current_top is None or abs(w["top"] - current_top) <= y_tolerance:
            current_line.append(w)
            current_top = w["top"] if current_top is None else current_top
        else:
            lines.append(current_line)
            current_line = [w]
            current_top = w["top"]
    if current_line:
        lines.append(current_line)

    return lines


def _line_words_to_text(line_words: List[dict]) -> str:
    return " ".join(w["text"] for w in sorted(line_words, key=lambda w: w["x0"]))


def _words_to_lines(words: List[dict], y_tolerance: float = 3.0) -> List[str]:
    """Groups words into text lines by vertical position, then orders each
    line left-to-right — reconstructing reading order within one column.
    """
    return [_line_words_to_text(line) for line in _group_words_into_lines(words, y_tolerance)]


def extract_hyperlinks_from_pdf(file_bytes: bytes) -> List[str]:
    """Extracts hyperlink target URIs (e.g. GitHub/LinkedIn buttons rendered
    as link-annotated text like "GitHub" with no visible URL) — these don't
    appear in plain extracted text, so URL_RE alone misses them.
    """
    import io

    links: List[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            for hyperlink in getattr(page, "hyperlinks", []):
                uri = hyperlink.get("uri")
                if uri:
                    links.append(uri)
    return links


_IGNORED_HEADER = "__ignored__"


def _match_section_header(line: str) -> str | None:
    normalized = line.strip().lower()
    if not normalized or len(normalized) > 60:
        return None
    for section, patterns in SECTION_HEADERS.items():
        for pattern in patterns:
            if re.match(pattern, normalized):
                return section
    for pattern in IGNORED_SECTION_HEADERS:
        if re.match(pattern, normalized):
            return _IGNORED_HEADER
    return None


def segment_sections(raw_text: str) -> Dict[str, List[str]]:
    """Split resume text into sections by detecting header lines."""
    lines = raw_text.splitlines()
    sections: Dict[str, List[str]] = {key: [] for key in SECTION_HEADERS}
    current_section: str | None = None

    for line in lines:
        matched = _match_section_header(line)
        if matched == _IGNORED_HEADER:
            current_section = None
            continue
        if matched:
            current_section = matched
            continue
        if current_section and line.strip():
            sections[current_section].append(line.strip())

    return sections


def extract_contact_info(raw_text: str) -> ContactInfo:
    email_match = EMAIL_RE.search(raw_text)
    phone_match = PHONE_RE.search(raw_text)
    first_line = raw_text.strip().splitlines()[0].strip() if raw_text.strip() else None
    name = first_line if first_line and len(first_line) < 60 and not EMAIL_RE.search(first_line) else None
    return ContactInfo(
        name=name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        location=None,
    )


def extract_links(raw_text: str) -> List[str]:
    return list(dict.fromkeys(URL_RE.findall(raw_text)))


def parse_skills(lines: List[str]) -> List[str]:
    skills: List[str] = []
    for line in lines:
        parts = re.split(r"[,;•|/]", line)
        for part in parts:
            cleaned = part.strip(" -\t")
            if cleaned and len(cleaned) < 60:
                skills.append(cleaned)
    return list(dict.fromkeys(skills))


def parse_bullet_group(lines: List[str]) -> List[Dict[str, str]]:
    """Groups lines under headers (assumed to be lines not starting with a bullet)
    into simple entries with 'header' and 'details' — pure structural heuristic,
    no content invention.
    """
    entries: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    for line in lines:
        is_bullet = line.startswith(("-", "•", "*")) or re.match(r"^\d+[.)]", line)
        if not is_bullet:
            if current:
                entries.append(current)
            current = {"header": line, "details": ""}
        else:
            if current is None:
                current = {"header": "", "details": ""}
            current["details"] = (current["details"] + " " + line).strip()
    if current:
        entries.append(current)
    return entries


def parse_resume_pdf(file_bytes: bytes) -> ParsedResumeData:
    """End-to-end: extract text, segment sections, structure output. No LLM call —
    pure deterministic extraction to avoid any hallucination risk.
    """
    raw_text = extract_text_from_pdf(file_bytes)
    sections = segment_sections(raw_text)
    contact = extract_contact_info(raw_text)
    links = list(dict.fromkeys(extract_links(raw_text) + extract_hyperlinks_from_pdf(file_bytes)))

    return ParsedResumeData(
        contact=contact,
        skills=parse_skills(sections["skills"]),
        experience=parse_bullet_group(sections["experience"]),
        education=parse_bullet_group(sections["education"]),
        projects=parse_bullet_group(sections["projects"]),
        certifications=[c.strip(" -\t") for c in sections["certifications"] if c.strip()],
        links=links,
    )
