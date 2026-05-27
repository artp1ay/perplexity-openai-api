default:
    @just --list

# Development
lint:
    uv run ruff check

format:
    uv run ruff format

self-test:
    uv run --active python -c "import json; import openai_server; print(json.dumps(openai_server.run_self_test(), ensure_ascii=False, indent=2))"

verify:
    uv run --active python scripts/verify_functionality.py --allow-tool-failures --pretty

verify-smoke:
    uv run --active python scripts/verify_functionality.py --skip-chat --pretty

# Server
serve:
    uv run python openai_server.py

health:
    curl -s http://localhost:8000/health | python -m json.tool

models:
    curl -s http://localhost:8000/v1/models | python -m json.tool

# Docker / Release
docker-build:
    docker compose build

docker-up:
    docker compose up -d

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f perplexity-api

docker-restart:
    docker compose restart perplexity-api

release-check: check self-test docker-build

test:
    uv run pytest -v

# Docker
build:
    docker-compose build

up:
    docker-compose up -d

down:
    docker-compose down

logs:
    docker-compose logs -f

restart:
    docker-compose restart

# Server
run:
    python openai_server.py

health:
    curl -s http://localhost:8000/health | python -m json.tool

models:
    curl -s http://localhost:8000/v1/models | python -m json.tool

# Setup
setup:
    cp .env.example .env
    @echo "Edit .env and add your PERPLEXITY_SESSION_TOKEN"
