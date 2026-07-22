"""Streamlit interface for the AI Data Analyst Agent."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import plotly.io as pio
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8010")
ROOT_DIR = Path(__file__).resolve().parents[1]

SAMPLE_DATASETS = {
    "Sales": {
        "path": ROOT_DIR / "data" / "sample_sales.csv",
        "icon": "🛒",
        "questions": [
            "Which product generated the highest revenue?",
            "Show monthly sales trends.",
            "Predict next month's sales.",
            "Give me a quick summary of the numeric columns.",
        ],
    },
    "Marketing": {
        "path": ROOT_DIR / "data" / "sample_marketing.csv",
        "icon": "📣",
        "questions": [
            "Which campaign generated the highest revenue?",
            "Show the monthly revenue trend.",
            "Predict next month's revenue.",
            "Give me a summary of the numeric columns.",
        ],
    },
    "Customer orders": {
        "path": ROOT_DIR / "data" / "sample_customer_orders.csv",
        "icon": "👥",
        "questions": [
            "Which customer generated the highest revenue?",
            "Show the monthly revenue trend.",
            "Predict next month's revenue.",
            "Give me a summary of the numeric columns.",
        ],
    },
    "Inventory": {
        "path": ROOT_DIR / "data" / "sample_inventory.csv",
        "icon": "📦",
        "questions": [
            "Which product generated the highest revenue?",
            "Show the monthly revenue trend.",
            "Predict next month's revenue.",
            "Give me a summary of the numeric columns.",
        ],
    },
}

DEFAULT_QUESTIONS = [
    "Which item generated the highest revenue?",
    "Show the monthly trend.",
    "Predict next month's value.",
    "Give me a summary of the numeric columns.",
]

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

    :root {
        --ink: #2a0b10;
        --muted: #7f4a52;
        --wine: #701323;
        --red: #c51f3a;
        --coral: #f05b62;
        --paper: #fffaf8;
        --line: rgba(142, 27, 47, 0.16);
    }

    [data-testid="stAppViewContainer"] {
        background:
            linear-gradient(rgba(119, 18, 37, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(119, 18, 37, 0.035) 1px, transparent 1px),
            radial-gradient(circle at 92% 7%, rgba(240, 91, 98, 0.22), transparent 28rem),
            linear-gradient(145deg, #fffaf8 0%, #fff0ed 52%, #fbd9d8 100%);
        background-size: 32px 32px, 32px 32px, auto, auto;
        background-attachment: fixed;
        color: var(--ink);
        font-family: "DM Sans", sans-serif;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 4rem;
        max-width: 1240px;
    }

    h1, h2, h3, .brand-name, .intro h1 {
        font-family: "Manrope", sans-serif;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.72rem 0 1.05rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 2.2rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 0.72rem;
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border-radius: 10px 10px 10px 2px;
        background: var(--wine);
        color: white;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.02em;
    }
    .brand-name {
        color: var(--ink);
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    .top-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--wine);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #e83d55;
        box-shadow: 0 0 0 5px rgba(232, 61, 85, 0.12);
    }

    .intro {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(260px, 0.55fr);
        gap: 4rem;
        align-items: end;
        margin-bottom: 2.8rem;
    }
    .eyebrow {
        color: var(--red);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .intro h1 {
        max-width: 760px;
        margin: 0;
        color: var(--ink);
        font-size: clamp(2.4rem, 5vw, 4.7rem);
        line-height: 0.98;
        letter-spacing: -0.065em;
    }
    .intro h1 em {
        color: var(--red);
        font-style: normal;
    }
    .intro-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
        padding-bottom: 0.25rem;
    }
    .intro-copy strong {
        color: var(--wine);
    }
    .workflow-line {
        margin-top: 1.1rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .workflow-line span {
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.55);
        border-radius: 6px;
        color: var(--wine);
        padding: 0.28rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .workspace-heading {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin: 0 0 0.9rem;
    }
    div[data-testid="stFileUploader"] {
        margin-top: 0;
        padding-top: 0;
    }
    div[data-testid="stFileUploader"] section {
        padding-top: 0;
    }
    .workspace-number {
        color: var(--red);
        font-family: "Manrope", sans-serif;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.1em;
    }
    .workspace-heading h2 {
        color: var(--ink);
        font-size: 1.15rem;
        letter-spacing: -0.03em;
        margin: 0 !important;
        padding: 0 !important;
    }
    .panel-copy {
        color: var(--muted);
        line-height: 1.65;
        max-width: 18rem;
        margin: 0 0 1rem;
    }
    .panel-note {
        border-left: 3px solid var(--coral);
        color: var(--wine);
        font-size: 0.82rem;
        padding: 0.1rem 0 0.1rem 0.8rem;
    }

    .ready-banner {
        background: var(--wine);
        color: #fff8f6;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        font-size: 0.95rem;
        margin: 0.6rem 0 0.9rem 0;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 250, 248, 0.78);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        box-shadow: 5px 5px 0 rgba(112, 19, 35, 0.08);
    }
    div[data-testid="stMetric"] label {
        color: var(--muted);
    }
    .stButton button, .stDownloadButton button {
        border-radius: 7px;
        font-weight: 700;
    }
    .stButton button[kind="secondary"],
    .stDownloadButton button {
        border: 1px solid var(--line);
        background: rgba(255, 250, 248, 0.74);
        color: var(--wine);
    }
    .stButton button[kind="secondary"]:hover,
    .stDownloadButton button:hover {
        border-color: var(--red);
        color: var(--red);
        background: #fff7f5;
    }
    section[data-testid="stFileUploaderDropzone"] {
        min-height: 145px;
        background:
            repeating-linear-gradient(-45deg, rgba(197,31,58,0.025) 0 8px, transparent 8px 16px),
            rgba(255, 250, 248, 0.8);
        border: 1px dashed rgba(112, 19, 35, 0.42);
        border-radius: 8px;
    }
    div[data-testid="stChatMessage"] {
        background: rgba(255, 250, 248, 0.78);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.6rem;
        box-shadow: 4px 4px 0 rgba(112, 19, 35, 0.06);
    }
    div[data-testid="stChatInput"] {
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(rgba(112,19,35,0.04) 1px, transparent 1px),
            #f8dedb;
        background-size: 100% 24px;
        border-right: 1px solid rgba(112, 19, 35, 0.16);
    }
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] strong,
    section[data-testid="stSidebar"] div {
        color: var(--ink);
    }
    section[data-testid="stSidebar"] .stButton button,
    section[data-testid="stSidebar"] .stDownloadButton button {
        border-radius: 6px;
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"],
    section[data-testid="stSidebar"] .stDownloadButton button {
        background: rgba(255, 250, 248, 0.7);
        border: 1px solid var(--line);
        color: var(--wine);
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover,
    section[data-testid="stSidebar"] .stDownloadButton button:hover {
        background: #fff8f6;
        border-color: var(--red);
        color: var(--red);
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--line);
    }
    details {
        border-radius: 8px !important;
        background: rgba(255, 250, 248, 0.72);
        border: 1px solid var(--line) !important;
    }
    hr {
        border-color: var(--line) !important;
    }
    @media (max-width: 760px) {
        .intro {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        .intro h1 {
            font-size: 2.65rem;
        }
        .top-status {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

for key, default in {
    "session_id": None,
    "messages": [],
    "summary": None,
    "dataset_name": None,
    "questions": DEFAULT_QUESTIONS,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def clear_chat() -> None:
    """Remove previous questions and answers from the UI."""
    st.session_state.messages = []


def upload_dataset(filename: str, content: bytes, questions: list[str]) -> None:
    """Upload a chosen file to FastAPI and reset the chat for the new dataset."""
    response = httpx.post(
        f"{API_URL}/upload",
        files={"file": (filename, content)},
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    st.session_state.session_id = data["session_id"]
    st.session_state.summary = data["summary"]
    st.session_state.dataset_name = data["filename"]
    st.session_state.questions = questions
    clear_chat()


# Sidebar: sample datasets and API status
with st.sidebar:
    st.markdown("### Sample datasets")
    st.caption("Load a prepared CSV to evaluate the analysis pipeline.")
    for title, sample in SAMPLE_DATASETS.items():
        sample_bytes = sample["path"].read_bytes()
        st.markdown(f"{sample['icon']} **{title}**")
        use_col, download_col = st.columns([3, 1])
        with use_col:
            if st.button(
                "Load dataset",
                key=f"use-{title}",
                type="primary",
                use_container_width=True,
                help=f"Load {sample['path'].name} for analysis",
            ):
                try:
                    upload_dataset(
                        sample["path"].name,
                        sample_bytes,
                        sample["questions"],
                    )
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Failed: {exc}")
        with download_col:
            st.download_button(
                "⬇️",
                data=sample_bytes,
                file_name=sample["path"].name,
                mime="text/csv",
                key=f"download-{title}",
                use_container_width=True,
                help=f"Download {sample['path'].name}",
            )

    st.divider()
    st.markdown("### API status")
    st.caption(f"Endpoint: {API_URL}")
    if st.button("Verify API connection", use_container_width=True):
        try:
            health = httpx.get(f"{API_URL}/health", timeout=10.0)
            health.raise_for_status()
            st.success("API is reachable")
        except Exception as exc:  # noqa: BLE001
            st.error(f"API is not reachable: {exc}")


# Header and introduction
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <span class="brand-mark">AI</span>
            <span class="brand-name">AI Data Analyst Agent</span>
        </div>
        <div class="top-status">
            <span class="status-dot"></span>
            Analysis session
        </div>
    </div>
    <div class="intro">
        <div>
            <div class="eyebrow">Natural-language analytical interface</div>
            <h1>Structured analysis from <em>tabular data.</em></h1>
        </div>
        <div class="intro-copy">
            Upload a CSV or Excel file and submit analytical questions in natural language.
            The system performs quantitative analysis, generates interactive visualizations,
            and returns an interpretable summary of the results.
            <div class="workflow-line">
                <span>UPLOAD</span><span>ANALYZE</span><span>INTERPRET</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dataset upload
setup_copy, setup_action = st.columns([0.75, 1.75], gap="large")
with setup_copy:
    st.markdown(
        """
        <div class="workspace-heading">
            <span class="workspace-number">01</span>
            <h2>Dataset input</h2>
        </div>
        <p class="panel-copy">Provide a tabular dataset in CSV or Excel format.
        The file is registered as an analysis session for subsequent queries.</p>
        <div class="panel-note">Sample datasets are available in the sidebar.</div>
        """,
        unsafe_allow_html=True,
    )
with setup_action:
    uploaded = st.file_uploader(
        "Upload dataset (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )
    if uploaded is not None and st.button(
        "Register dataset",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner("Registering dataset..."):
                upload_dataset(uploaded.name, uploaded.getvalue(), DEFAULT_QUESTIONS)
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Upload failed: {exc}")

    if st.session_state.summary:
        summary = st.session_state.summary
        st.markdown(
            f'<div class="ready-banner">● &nbsp; Active dataset &nbsp; '
            f"<strong>{st.session_state.dataset_name}</strong></div>",
            unsafe_allow_html=True,
        )
        metric_columns = st.columns(3)
        metric_columns[0].metric("Rows", summary["rows"])
        metric_columns[1].metric("Columns", len(summary["columns"]))
        metric_columns[2].metric(
            "Numeric columns",
            len(summary.get("numeric_columns", [])),
        )
        with st.expander("Column schema"):
            st.code(", ".join(summary["columns"]))

st.divider()

# Query interface
st.markdown(
    """
    <div class="workspace-heading">
        <span class="workspace-number">02</span>
        <h2>Analytical query</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.session_id:
    st.info("Upload a dataset above, or load a sample from the sidebar, to begin analysis.")
else:
    st.caption("Select a suggested query or enter a custom analytical question below.")
    question_columns = st.columns(4)
    for index, example in enumerate(st.session_state.questions):
        with question_columns[index % 4]:
            if st.button(example, use_container_width=True):
                st.session_state["prefill"] = example

question = st.chat_input(
    "Enter an analytical question...",
    disabled=not st.session_state.session_id,
)
if st.session_state.get("prefill"):
    question = st.session_state.pop("prefill")

for index, message in enumerate(st.session_state.messages):
    avatar = "🧑‍💼" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message.get("chart_json"):
            fig = pio.from_json(message["chart_json"])
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"history-chart-{index}",
            )
        if message.get("steps"):
            with st.expander("Agent steps"):
                for step in message["steps"]:
                    st.write(f"- {step}")
                if message.get("mode"):
                    st.caption(f"Mode: {message['mode']}")

if st.session_state.session_id and st.session_state.messages:
    if st.button(
        "Clear conversation",
        help="Remove prior queries and responses from this session",
    ):
        clear_chat()
        st.rerun()

if question and st.session_state.session_id:
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Running analysis..."):
            response = httpx.post(
                f"{API_URL}/ask",
                json={
                    "session_id": st.session_state.session_id,
                    "question": question,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            chart_json = None
            if data.get("chart") and data["chart"].get("plotly_json"):
                chart_json = data["chart"]["plotly_json"]
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": data["answer"],
                    "chart_json": chart_json,
                    "steps": data.get("steps", []),
                    "mode": data.get("mode"),
                }
            )
    except Exception as exc:  # noqa: BLE001
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Analysis failed: {exc}",
            }
        )
    st.rerun()
