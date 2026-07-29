"""Builds and compiles the LangGraph StateGraph for the job-application agent.

Flow:
    extract_fields -> extract_jd -> retrieve_context -> semantic_matching
    -> generate_answers -> validate
        --(errors, retries left)--> increment_retry -> generate_answers (loop)
        --(no errors / retries exhausted)--> human_approval (interrupt)
    human_approval --(approved)--> submit -> save_history -> END
    human_approval --(rejected/other)--> save_history -> END
"""
from __future__ import annotations

from typing import Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.agents.nodes.extract_fields import extract_fields_node
from app.agents.nodes.extract_jd import make_extract_jd_node
from app.agents.nodes.generate_answers import make_generate_answers_node
from app.agents.nodes.human_approval import human_approval_node, route_after_approval
from app.agents.nodes.retrieve_context import make_retrieve_context_node
from app.agents.nodes.save_history import make_save_history_node
from app.agents.nodes.semantic_matching import make_semantic_matching_node
from app.agents.nodes.submit import make_submit_node
from app.agents.nodes.validate import increment_retry_node, route_after_validate, validate_node
from app.agents.state import AgentState
from app.agents.tools.playwright_tool import PlaywrightTool
from app.llm.client import LLMClient
from app.services.answer_generation_service import AnswerGenerationService
from app.services.retriever_service import RetrieverService


def build_graph(
    *,
    llm_client: LLMClient,
    retriever_service: RetrieverService,
    answer_service: AnswerGenerationService,
    db_session,
    playwright_tool: Optional[PlaywrightTool] = None,
    checkpointer: Optional[BaseCheckpointSaver] = None,
):
    """Constructs the compiled LangGraph app. `db_session` is an AsyncSession
    used by the save_history node to persist results.
    """
    graph = StateGraph(AgentState)

    graph.add_node("extract_fields", extract_fields_node)
    graph.add_node("extract_jd", make_extract_jd_node(llm_client))
    graph.add_node("retrieve_context", make_retrieve_context_node(retriever_service))
    graph.add_node("semantic_matching", make_semantic_matching_node(llm_client))
    graph.add_node("generate_answers", make_generate_answers_node(answer_service))
    graph.add_node("validate", validate_node)
    graph.add_node("increment_retry", increment_retry_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("submit", make_submit_node(playwright_tool))
    graph.add_node("save_history", make_save_history_node(db_session))

    graph.add_edge(START, "extract_fields")
    graph.add_edge("extract_fields", "extract_jd")
    graph.add_edge("extract_jd", "retrieve_context")
    graph.add_edge("retrieve_context", "semantic_matching")
    graph.add_edge("semantic_matching", "generate_answers")
    graph.add_edge("generate_answers", "validate")

    graph.add_conditional_edges(
        "validate",
        route_after_validate,
        {"retry": "increment_retry", "human_approval": "human_approval"},
    )
    graph.add_edge("increment_retry", "generate_answers")

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {"submit": "submit", "save_history": "save_history"},
    )
    graph.add_edge("submit", "save_history")
    graph.add_edge("save_history", END)

    return graph.compile(checkpointer=checkpointer)
