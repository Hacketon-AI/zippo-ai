# Migration Plan from Old Python Backend

## Strategy

Do not refactor the old project directly.

Use this approach:

```text
Create new clean project
↓
Copy only useful logic from old backend
↓
Migrate module by module
↓
Test every module
↓
Delete unused legacy logic
```

## Migration Phases

### Phase 1 — Identify Old Logic

Find:

- Ollama client logic.
- Existing prompt logic.
- Existing chat endpoint.
- Existing memory/database logic.
- Any useful utility functions.

### Phase 2 — Move Ollama Client

Target:

```text
api/app/services/ollama_service.py
```

### Phase 3 — Move Chat Logic

Target:

```text
api/app/services/assistant_service.py
api/app/routes/chat.py
```

### Phase 4 — Add Cache

Target:

```text
api/app/services/cache_service.py
api/app/db/models.py
```

### Phase 5 — Add Qdrant Memory

Target:

```text
api/app/services/qdrant_service.py
api/app/services/memory_service.py
```

### Phase 6 — Add Feedback Learning

Target:

```text
api/app/routes/feedback.py
api/app/services/feedback_service.py
```
