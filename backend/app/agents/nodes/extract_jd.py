"""Node: extract structured fields from job description text via LLM."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.agents.state import AgentState
from app.llm.client import LLMClient
from app.llm.prompts import jd_extraction_prompt

logger = logging.getLogger("app.agents.extract_jd")


class JDExtraction(BaseModel):
    company: Optional[str] = None
    role_title: Optional[str] = None
    skills: List[str] = []
    responsibilities: List[str] = []
    requirements: List[str] = []
    nice_to_have: List[str] = []
    experience_required: Optional[str] = None


async def extract_jd_node(state: AgentState, llm_client: LLMClient) -> Dict[str, Any]:
    jd_text = state.get("job_description", "")
    if not jd_text:
        return {"jd_extracted": {}}

    messages = jd_extraction_prompt(jd_text)
    try:
        result = await llm_client.structured_chat(messages, JDExtraction)
        return {"jd_extracted": result.model_dump()}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("JD extraction failed: %s", exc)
        return {
            "jd_extracted": {},
            "errors": state.get("errors", []) + [f"JD extraction failed: {exc}"],
        }


def make_extract_jd_node(llm_client: LLMClient):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await extract_jd_node(state, llm_client)

    return _node
