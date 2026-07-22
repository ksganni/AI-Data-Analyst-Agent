"""LangGraph workflow for the AI Data Analyst Agent.

Flow:
1) load_data
2) analyze
3) visualize
4) explain
"""

from __future__ import annotations

from typing import Any

import httpx
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.config import get_settings
from app.tools.analytics import run_analysis
from app.tools.data_loader import dataset_summary, load_dataset
from app.tools.visualization import chart_from_analysis


def load_data_node(state: AgentState) -> dict[str, Any]:
    df = load_dataset(state["file_path"])
    summary = dataset_summary(df)
    steps = list(state.get("steps", []))
    steps.append("Loaded dataset and created schema summary")
    return {"summary": summary, "steps": steps}


def analyze_node(state: AgentState) -> dict[str, Any]:
    df = load_dataset(state["file_path"])
    analysis = run_analysis(df, state["question"])
    steps = list(state.get("steps", []))
    steps.append(f"Ran analysis tool: {analysis.get('tool')}")
    return {"analysis": analysis, "steps": steps}


def visualize_node(state: AgentState) -> dict[str, Any]:
    chart = chart_from_analysis(state.get("analysis", {}))
    steps = list(state.get("steps", []))
    steps.append("Created chart" if chart else "No chart needed for this question")
    return {"chart": chart, "steps": steps}


def _gemini_explain(question: str, columns: list[str] | None, analysis: dict[str, Any]) -> str:
    """Call Google Gemini free-tier HTTP API for optional wording."""
    settings = get_settings()
    prompt = (
        "You are a helpful business data analyst. "
        "Explain the finding clearly for a non-technical user. "
        "Keep it under 120 words.\n\n"
        f"Question: {question}\n"
        f"Dataset columns: {columns}\n"
        f"Tool result: {analysis}\n"
    )
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    response = httpx.post(
        url,
        params={"key": settings.gemini_api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60.0,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["candidates"][0]["content"]["parts"][0]["text"]


def explain_node(state: AgentState) -> dict[str, Any]:
    """Produce the final analytical explanation.

    Prefer Google Gemini when a key exists. If its free quota is exhausted or
    the service is unavailable, return the exact local analysis-tool answer.
    """
    settings = get_settings()
    analysis = state.get("analysis", {})
    base_answer = analysis.get("answer", "Analysis complete.")
    steps = list(state.get("steps", []))

    if settings.has_gemini:
        try:
            answer = _gemini_explain(
                state["question"],
                state.get("summary", {}).get("columns"),
                analysis,
            )
            mode = "gemini"
            steps.append("Generated explanation with Google Gemini free tier")
        except httpx.HTTPStatusError as exc:
            answer = base_answer
            mode = "local_fallback"
            if exc.response.status_code == 429:
                steps.append(
                    "Gemini free-tier limit reached; used the normal local answer"
                )
            else:
                steps.append(
                    "Gemini was unavailable; used the normal local answer"
                )
        except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError):
            answer = base_answer
            mode = "local_fallback"
            steps.append("Gemini was unavailable; used the normal local answer")
    else:
        answer = base_answer
        mode = "rule_based"
        steps.append("Used the analysis tool's answer (no Gemini key configured)")

    return {"answer": answer, "steps": steps, "mode": mode}


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("load_data", load_data_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("visualize", visualize_node)
    graph.add_node("explain", explain_node)

    graph.set_entry_point("load_data")
    graph.add_edge("load_data", "analyze")
    graph.add_edge("analyze", "visualize")
    graph.add_edge("visualize", "explain")
    graph.add_edge("explain", END)
    return graph.compile()


_AGENT = None


def get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = build_agent()
    return _AGENT


def run_agent(question: str, file_path: str) -> dict[str, Any]:
    agent = get_agent()
    return agent.invoke(
        {
            "question": question,
            "file_path": file_path,
            "steps": [],
        }
    )
