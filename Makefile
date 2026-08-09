.PHONY: up down migrate run-api run-worker run-ui test

up:
	docker compose up -d

down:
	docker compose down

migrate:
	alembic upgrade head

run-api:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	python -m apps.worker.main

run-ui:
	streamlit run apps/streamlit_app/app.py

test:
	pytest -m "not e2e"
