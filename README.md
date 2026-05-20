# Personal AI Assistant

Local-first personal AI assistant. Backend skeleton built with FastAPI, designed to run on a small VPS (Hostinger KVM 2) using Docker Compose alongside PostgreSQL, Qdrant, and Ollama (Qwen3).

See `docs/PRD.md` for the full product spec and `CLAUDE.md` for development rules.

## Status

Phase 2 — Skeleton + chat endpoint backed by local Ollama.

## Stack

- Python 3.11 + FastAPI
- PostgreSQL 16
- Qdrant
- Ollama (Qwen3 default `qwen3:4b`)
- Docker Compose

## Project Layout

```text
api/
  Dockerfile
  requirements.txt
  app/
    main.py
    core/config.py
    routes/health.py
docker-compose.yml
.env.example
Makefile
```

## Setup

1. Copy env file:

   ```bash
   cp .env.example .env
   ```

2. Build and start services:

   ```bash
   make up
   # or
   docker compose up -d
   ```

3. Check container status:

   ```bash
   docker compose ps
   ```

## Test the health endpoint

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{ "status": "ok", "service": "personal-ai-assistant" }
```

## Stop services

```bash
make down
```

## Environment variables

Ollama (active, read by `api/app/core/config.py`):

```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_DEFAULT_MODEL=qwen3:4b
OLLAMA_TIMEOUT_SECONDS=60
```

Legacy keys `OLLAMA_HOST`, `OLLAMA_PORT`, and `OLLAMA_MODEL` are deprecated and ignored. See `.env.example` for the full template.

## Notes

- Ollama port is internal-only and is not exposed to the host or public network.
- PostgreSQL and Qdrant ports are bound to `127.0.0.1` only.
- Open WebUI is provided as an optional, commented service in `docker-compose.yml`.
- Do not commit `.env`. Use `.env.example` as the template.
