#!/usr/bin/env bash
set -euo pipefail

uvicorn app.api.main:app --host 0.0.0.0 --port 8010 &
API_URL=http://localhost:8010 streamlit run frontend/streamlit_app.py --server.port 8510 --server.address 0.0.0.0
