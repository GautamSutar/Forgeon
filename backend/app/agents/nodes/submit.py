"""Node: mark application as submitted and invoke the Playwright tool's
fill+submit actions. Only ever reached after human_approval resolves to
"approved" — this node re-asserts that guard explicitly and raises if
violated, regardless of graph wiring.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.agents.state import AgentState
from app.agents.tools.playwright_tool import ApprovalNotGrantedError, PlaywrightTool

logger = logging.getLogger("app.agents.submit")


async def submit_node(state: AgentState, playwright_tool: Optional[PlaywrightTool] = None) -> Dict[str, Any]:
    approval_status = state.get("approval_status")
    if approval_status != "approved":
        raise ApprovalNotGrantedError(
            f"submit_node invoked without approval (approval_status={approval_status!r}). "
            "Refusing to submit application."
        )

    approved_answers = state.get("approved_answers", {})
    fields = state.get("extracted_fields", [])

    if playwright_tool is not None:
        field_actions = []
        for field in fields:
            field_key = field.get("name") or field.get("label") or ""
            value = approved_answers.get(field_key)
            if value is None or not field.get("css"):
                continue
            field_actions.append({"selector": field["css"], "type": field.get("type", "text"), "value": value})

        try:
            await playwright_tool.fill_form(field_actions)
            submit_selector = "button[type='submit'], input[type='submit']"
            await playwright_tool.submit_form(submit_selector, approved=True)
        except ApprovalNotGrantedError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Playwright submission failed: %s", exc)
            return {"application_status": "failed", "errors": state.get("errors", []) + [str(exc)]}

    return {"application_status": "submitted"}


def make_submit_node(playwright_tool: Optional[PlaywrightTool] = None):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await submit_node(state, playwright_tool)

    return _node
