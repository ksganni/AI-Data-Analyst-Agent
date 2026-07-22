"""Shared state for the LangGraph agent workflow."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    file_path: str
    summary: dict[str, Any]
    analysis: dict[str, Any]
    chart: dict[str, Any] | None
    answer: str
    steps: list[str]
    mode: str
