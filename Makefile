.PHONY: help install dev api worker migrate contracts infra-up infra-down lint format test typecheck

help:
	@echo "Country Decision Atlas"
	@echo ""
	@echo "Common targets:"
	@echo "  make install     Install Python and frontend dependencies"
	@echo "  make dev         Start local API and frontend in separate terminals manually"
	@echo "  make api         Run the FastAPI app"
	@echo "  make worker      Run the worker placeholder"
	@echo "  make migrate     Apply SQL migrations"
	@echo "  make contracts   Generate TypeScript contracts from OpenAPI"
	@echo "  make infra-up    Start local infrastructure services"
	@echo "  make infra-down  Stop local infrastructure services"
	@echo "  make lint        Run Python and frontend linters"
	@echo "  make format      Format Python and frontend files"
	@echo "  make test        Run Python tests"

install:
	python -m pip install -e ".[dev]"
	pnpm install

dev:
	@echo "Run 'make infra-up', then run 'make api' and 'pnpm dev' in separate terminals."

api:
	python -m uvicorn app.main:app --app-dir apps/api --reload

worker:
	python apps/worker/main.py

migrate:
	python scripts/apply_migrations.py

contracts:
	pnpm contracts:generate

infra-up:
	docker compose up -d postgres redis

infra-down:
	docker compose down

lint:
	python -m ruff check apps packages scripts
	pnpm lint

format:
	python -m ruff format apps packages scripts
	python -m ruff check --fix apps packages scripts
	pnpm format

test:
	python -m pytest

typecheck:
	python -m mypy apps packages
	pnpm typecheck
