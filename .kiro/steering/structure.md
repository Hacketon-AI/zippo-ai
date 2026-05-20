# Structure Steering

Backend must use Python FastAPI.

Folder rules:
- `routes/` contains HTTP endpoints only.
- `schemas/` contains Pydantic request/response models.
- `services/` contains business logic.
- `db/` contains SQLAlchemy models/session/migrations.
- `core/` contains config/security/logging.
- `prompts/` contains prompt templates.
- `tests/` contains automated tests.

Do not put business logic in route files.
