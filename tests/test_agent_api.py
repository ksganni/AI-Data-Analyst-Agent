from pathlib import Path
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from app.agent import graph
from app.api.main import app

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_and_ask():
    with SAMPLE.open("rb") as handle:
        upload = client.post(
            "/upload",
            files={"file": ("sample_sales.csv", handle, "text/csv")},
        )
    assert upload.status_code == 200
    session_id = upload.json()["session_id"]
    assert upload.json()["summary"]["rows"] > 0

    ask = client.post(
        "/ask",
        json={
            "session_id": session_id,
            "question": "Which product generated the highest revenue?",
        },
    )
    assert ask.status_code == 200
    payload = ask.json()
    assert "Widget C" in payload["answer"]
    assert payload["steps"]
    assert payload["chart"] is not None


def test_ask_unknown_session():
    response = client.post(
        "/ask",
        json={"session_id": "does-not-exist", "question": "hello"},
    )
    assert response.status_code == 404


def test_gemini_quota_limit_uses_local_answer(monkeypatch):
    monkeypatch.setattr(
        graph,
        "get_settings",
        lambda: SimpleNamespace(has_gemini=True),
    )

    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(429, request=request)

    def quota_error(*args, **kwargs):
        raise httpx.HTTPStatusError(
            "quota exceeded",
            request=request,
            response=response,
        )

    monkeypatch.setattr(graph, "_gemini_explain", quota_error)
    result = graph.explain_node(
        {
            "question": "Which product is best?",
            "analysis": {"answer": "Widget C is best."},
            "summary": {"columns": ["product", "revenue"]},
            "steps": [],
        }
    )

    assert result["answer"] == "Widget C is best."
    assert result["mode"] == "local_fallback"
    assert "limit reached" in result["steps"][-1]
