"""FastAPI backend for uploads and agent questions."""

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.graph import run_agent
from app.config import get_settings
from app.tools.data_loader import SUPPORTED_EXTENSIONS, dataset_summary, load_dataset

app = FastAPI(
    title="AI Data Analyst Agent",
    description="Upload structured business data and submit analytical queries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory registry of uploaded files for this demo app
SESSIONS: dict[str, dict[str, Any]] = {}


class AskRequest(BaseModel):
    session_id: str
    question: str


class AskResponse(BaseModel):
    session_id: str
    answer: str
    steps: list[str]
    mode: str
    analysis: dict[str, Any]
    chart: dict[str, Any] | None = None
    summary: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, Any]:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported.")

    session_id = str(uuid4())
    save_path = settings.upload_path / f"{session_id}{suffix}"
    content = await file.read()
    save_path.write_bytes(content)

    try:
        df = load_dataset(save_path)
        summary = dataset_summary(df)
    except Exception as exc:  # noqa: BLE001
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not read file: {exc}") from exc

    SESSIONS[session_id] = {
        "file_path": str(save_path),
        "filename": file.filename,
        "summary": summary,
    }
    return {
        "session_id": session_id,
        "filename": file.filename,
        "summary": summary,
    }


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    session = SESSIONS.get(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Unknown session_id. Upload a file first.")

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_agent(payload.question, session["file_path"])
    return AskResponse(
        session_id=payload.session_id,
        answer=result.get("answer", ""),
        steps=result.get("steps", []),
        mode=result.get("mode", "unknown"),
        analysis=result.get("analysis", {}),
        chart=result.get("chart"),
        summary=result.get("summary", session["summary"]),
    )


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "filename": session["filename"],
        "summary": session["summary"],
    }
