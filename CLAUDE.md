# CLAUDE.md — Project Instructions for Personal AI Assistant

## Project Summary

This project is a local-first personal AI assistant built with Python FastAPI, Ollama, Qwen3, PostgreSQL, Qdrant, and Docker Compose.

The assistant must run on a small VPS and must prioritize local memory/cache before using any external AI API.

## Main Goals

- Build a clean, modular, production-minded FastAPI backend.
- Use Ollama + Qwen3 as the default local LLM.
- Use PostgreSQL for exact cache, chat history, feedback, and metadata.
- Use Qdrant for semantic memory and RAG.
- Use Docker Compose for local/VPS deployment.
- Minimize API/token usage.
- Keep the code clean, testable, and easy to refactor.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Qdrant
- Ollama
- Qwen3 default model: `qwen3:4b`
- Optional model: `qwen3:8b` only if VPS memory allows
- Docker Compose

## Architecture Rules

Follow this structure:

- `routes/`: HTTP endpoint layer only.
- `schemas/`: Pydantic request/response models.
- `services/`: business logic.
- `db/`: SQLAlchemy models, session, migrations.
- `prompts/`: prompt templates.
- `utils/`: small pure helper functions.
- `tests/`: automated tests.

Never put business logic inside route files.

## Development Rules

- Work one task at a time.
- Do not scan or rewrite the entire repository unless explicitly asked.
- Before editing, list the files you will create or modify.
- Make minimal changes.
- Do not change unrelated files.
- Prefer small, reviewable diffs.
- Keep code readable and simple.
- Use type hints.
- Use Pydantic models for API input/output.
- Use environment variables for configuration.
- Do not hardcode secrets.
- Do not add unnecessary dependencies.
- Update docs only when the change affects behavior or setup.

## Token Saving Rules

The user has limited Kiro/Claude credits. Be efficient.

- Read only relevant files.
- Do not open the full repository unless asked.
- Do not generate long explanations unless requested.
- Avoid repeating the PRD content.
- Do not regenerate working files.
- If context is missing, ask for the specific missing file only.
- One prompt should solve one small task.
- Summarize changes briefly after implementation.

## AI Flow Rules

The assistant must follow this priority:

1. Correction memory.
2. PostgreSQL exact cache.
3. Qdrant semantic memory.
4. Local Qwen3 via Ollama.
5. External API fallback only if allowed and necessary.

External API must not be used if local cache or memory is enough.

## Security Rules

- Never expose Ollama port publicly.
- Never commit `.env`.
- Never log API keys.
- Never hardcode credentials.
- Use `.env.example` for config examples.
- Use Nginx/SSL for production access.
- Upload endpoints must validate file type and file size.

## Testing Rules

When implementing a service, add or update tests when practical.

Minimum expected tests:

- Health endpoint.
- Chat endpoint basic flow.
- Cache service.
- Memory/Qdrant service where possible.
- Feedback service.

## Docker Rules

- Keep Docker Compose simple.
- Services should include: api, postgres, qdrant, ollama, open-webui optional.
- Do not expose internal ports publicly unless needed.
- Use named volumes for persistent data.

## Response Format When Working

Before changes:

```text
I will modify/create:
- file 1
- file 2

Reason:
- short reason
```

After changes:

```text
Done.
Changed:
- file 1: summary
- file 2: summary

Test/Run:
- command used or recommended
```

