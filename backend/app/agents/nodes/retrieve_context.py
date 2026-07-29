"""Node: retrieve resume/profile/answer chunks relevant to the form fields + JD."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

from app.agents.state import AgentState
from app.services.retriever_service import RetrieverService

logger = logging.getLogger("app.agents.retrieve_context")


async def retrieve_context_node(state: AgentState, retriever_service: RetrieverService) -> Dict[str, Any]:
    user_id_raw = state.get("user_id")
    if not user_id_raw:
        return {"retrieved_context": []}

    try:
        user_id = uuid.UUID(user_id_raw)
    except (ValueError, TypeError):
        return {"retrieved_context": []}

    jd_text = state.get("job_description", "")
    field_labels = [f.get("label") or f.get("name") or "" for f in state.get("extracted_fields", [])]
    query = " ".join([jd_text[:2000]] + [lbl for lbl in field_labels if lbl])
    if not query.strip():
        return {"retrieved_context": []}

    try:
        context: List[str] = await retriever_service.retrieve_text(user_id=user_id, query=query, top_k=8)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Retrieval failed: %s", exc)
        context = []

    return {"retrieved_context": context}


def make_retrieve_context_node(retriever_service: RetrieverService):
    async def _node(state: AgentState) -> Dict[str, Any]:
        return await retrieve_context_node(state, retriever_service)

    return _node
