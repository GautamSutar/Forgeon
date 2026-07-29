"""Generic HTML form field extractor using BeautifulSoup."""
from __future__ import annotations

from typing import List, Optional

from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel


class FormField(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    xpath: Optional[str] = None
    css: Optional[str] = None
    type: str
    required: bool = False
    options: List[str] = []
    placeholder: Optional[str] = None
    tag_id: Optional[str] = None


def _element_css(el: Tag) -> str:
    parts = [el.name]
    if el.get("id"):
        parts.append(f"#{el['id']}")
    if el.get("name"):
        parts.append(f"[name='{el['name']}']")
    return "".join(parts)


def _find_label_for(soup: BeautifulSoup, el: Tag) -> Optional[str]:
    el_id = el.get("id")
    if el_id:
        label_tag = soup.find("label", attrs={"for": el_id})
        if label_tag:
            return label_tag.get_text(strip=True)
    parent_label = el.find_parent("label")
    if parent_label:
        return parent_label.get_text(strip=True)
    if el.get("aria-label"):
        return el.get("aria-label")
    if el.get("placeholder"):
        return el.get("placeholder")
    next_text = el.next_sibling
    if isinstance(next_text, str) and next_text.strip():
        return next_text.strip()
    return None


def parse_html_form(html: str) -> List[FormField]:
    """Extract structured form fields from raw HTML."""
    soup = BeautifulSoup(html, "html.parser")
    fields: List[FormField] = []

    seen_radio_groups = set()

    for el in soup.find_all(["input", "textarea", "select"]):
        el_type = el.get("type", "text") if el.name == "input" else el.name
        if el_type in ("hidden", "submit", "button", "image", "reset"):
            continue

        name = el.get("name")
        if el_type == "radio" and name:
            if name in seen_radio_groups:
                continue
            seen_radio_groups.add(name)

        label = _find_label_for(soup, el)
        required = el.has_attr("required") or el.get("aria-required") == "true"
        placeholder = el.get("placeholder")

        options: List[str] = []
        if el.name == "select":
            options = [opt.get_text(strip=True) for opt in el.find_all("option")]
        elif el_type in ("radio", "checkbox") and name:
            siblings = soup.find_all("input", attrs={"name": name, "type": el_type})
            options = [
                _find_label_for(soup, sib) or sib.get("value", "")
                for sib in siblings
            ]

        fields.append(
            FormField(
                name=name,
                label=label,
                css=_element_css(el),
                type=el_type,
                required=required,
                options=options,
                placeholder=placeholder,
                tag_id=el.get("id"),
            )
        )

    return fields
