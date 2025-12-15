default:
    @just --list

# Development
lint:
    uv run ruff check

format:
    uv run ruff format

install:
    uv sync --upgrade --all-extras --all-groups

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
