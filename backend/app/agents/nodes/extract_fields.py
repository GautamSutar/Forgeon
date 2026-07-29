"""Node: parse raw form HTML into structured FormField list."""
from __future__ import annotations

import logging
from typing import Any, Dict

from app.agents.state import AgentState
from app.parsers.html_form_parser import parse_html_form

logger = logging.getLogger("app.agents.extract_fields")


async def extract_fields_node(state: AgentState) -> Dict[str, Any]:
    html = state.get("html", "")
    if not html:
        return {"extracted_fields": [], "errors": state.get("errors", []) + ["No HTML provided to extract_fields"]}

    fields = parse_html_form(html)
    return {"extracted_fields": [f.model_dump() for f in fields]}
