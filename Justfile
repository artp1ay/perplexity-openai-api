default:
    @just --list

# Development
lint:
    uv run ruff check

format:
    uv run ruff format

test:
    uv run pytest -v

# Testing & Verification
self-test:
    uv run --active python -c "import json; import openai_server; print(json.dumps(openai_server.run_self_test(), ensure_ascii=False, indent=2))"

verify:
    uv run --active python scripts/verify_functionality.py --allow-tool-failures --pretty

verify-smoke:
    uv run --active python scripts/verify_functionality.py --skip-chat --pretty

# Server
serve:
    uv run python openai_server.py

run:
    python openai_server.py

health:
    curl -s http://localhost:8000/health | python -m json.tool

models:
    curl -s http://localhost:8000/v1/models | python -m json.tool

# Docker
build:
    docker compose build

up:
    docker compose up -d

down:
    docker compose down

logs:
    docker compose logs -f perplexity-api

restart:
    docker compose restart perplexity-api

release-check: self-test build

# Setup
setup:
    cp .env.example .env
    @echo "Edit .env and add your PERPLEXITY_SESSION_TOKEN"
