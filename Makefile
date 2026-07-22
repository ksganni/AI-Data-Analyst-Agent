.PHONY: setup test api ui docker-up docker-down clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	cp -n .env.example .env || true
	@echo "Setup done. Optional: add a free GEMINI_API_KEY from Google AI Studio."

test:
	. .venv/bin/activate && pytest

api:
	. .venv/bin/activate && uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8010

ui:
	. .venv/bin/activate && API_URL=http://localhost:8010 streamlit run frontend/streamlit_app.py --server.port 8510

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	rm -rf .venv .pytest_cache **/__pycache__
