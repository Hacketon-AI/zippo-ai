# Kiro Prompt Pack — Hemat Kredit untuk Build Personal AI Assistant

Gunakan prompt ini satu per satu. Jangan jalankan semua sekaligus.

## Aturan Umum Saat Prompting

Tambahkan kalimat ini di awal setiap prompt jika perlu:

```text
Read CLAUDE.md and only the relevant .kiro/steering file. Do not scan the whole repository. Before editing, list files you will create or modify. Keep the change minimal.
```

---

## Prompt 0 — Setup Project Files Only

```text
Read CLAUDE.md and docs/PRD.md.
Task: Create only the initial project skeleton.

Create:
- api/app/main.py
- api/app/routes/health.py
- api/app/core/config.py
- api/requirements.txt
- api/Dockerfile
- docker-compose.yml
- .env.example

Rules:
- Do not implement chat yet.
- Do not implement database models yet.
- Do not implement Qdrant yet.
- Keep code minimal and clean.
- Before editing, list all files you will create.
```

---

## Prompt 1 — Health Endpoint

```text
Read only:
- CLAUDE.md
- .kiro/steering/structure.md
- api/app/main.py
- api/app/routes/health.py

Task: Ensure FastAPI health endpoint works at GET /api/v1/health.

Do not modify unrelated files.
Return only changed files summary and test command.
```

---

## Prompt 2 — Ollama Service

```text
Read only:
- CLAUDE.md
- .kiro/steering/tech.md
- api/app/core/config.py

Task: Create Ollama client service.

Create:
- api/app/services/ollama_service.py

Requirements:
- Use async httpx.
- Read OLLAMA_BASE_URL and OLLAMA_DEFAULT_MODEL from config.
- Implement generate_chat(message: str, context: str | None = None).
- Handle timeout and API errors cleanly.
- Do not add business logic.
- Do not modify routes yet.

Before editing, list files to create/modify.
```

---

## Prompt 3 — Basic Chat Endpoint

```text
Read only:
- CLAUDE.md
- .kiro/steering/structure.md
- api/app/services/ollama_service.py
- api/app/main.py

Task: Add basic POST /api/v1/chat without cache and without Qdrant.

Create/modify only:
- api/app/schemas/chat.py
- api/app/services/assistant_service.py
- api/app/routes/chat.py
- api/app/main.py if route registration is needed

Flow:
1. Receive user message.
2. Call assistant_service.
3. assistant_service calls ollama_service.
4. Return answer.

Do not implement database, cache, Qdrant, or fallback API.
```

---

## Prompt 4 — PostgreSQL Models and Session

```text
Read only:
- CLAUDE.md
- .kiro/steering/tech.md
- docs/PRD.md database section
- api/app/core/config.py

Task: Add PostgreSQL database session and initial models.

Create/modify:
- api/app/db/session.py
- api/app/db/models.py
- api/requirements.txt if needed

Models:
- ConversationSession
- ChatMessage
- AiCache
- FeedbackCorrection
- KnowledgeDocument

Do not integrate into chat flow yet.
Keep implementation minimal.
```

---

## Prompt 5 — Exact Cache Service

```text
Read only:
- CLAUDE.md
- .kiro/steering/clean-code.md
- api/app/db/models.py
- api/app/db/session.py
- api/app/services/assistant_service.py

Task: Add exact cache service and integrate it into chat flow.

Create/modify only:
- api/app/services/cache_service.py
- api/app/services/assistant_service.py
- api/app/utils/text_normalizer.py

Flow:
1. Normalize question.
2. Check cache by question hash.
3. If valid cache exists, return cached answer.
4. If not, call Ollama.
5. Save answer to cache.

Do not implement Qdrant yet.
Do not implement external fallback.
```

---

## Prompt 6 — Qdrant Service Only

```text
Read only:
- CLAUDE.md
- .kiro/steering/tech.md
- api/app/core/config.py

Task: Create Qdrant service only.

Create:
- api/app/services/qdrant_service.py
- api/app/services/embedding_service.py

Requirements:
- embedding_service calls Ollama embedding model.
- qdrant_service can create collection if missing.
- qdrant_service can search and upsert memory.
- Do not integrate into chat flow yet.
```

---

## Prompt 7 — Integrate Semantic Memory

```text
Read only:
- CLAUDE.md
- .kiro/steering/structure.md
- api/app/services/assistant_service.py
- api/app/services/qdrant_service.py
- api/app/services/embedding_service.py
- api/app/services/cache_service.py

Task: Integrate Qdrant semantic memory into chat flow.

Flow priority:
1. Exact cache.
2. Qdrant semantic memory.
3. Ollama local answer.
4. Save final useful answer to cache and Qdrant.

Do not implement external fallback yet.
Keep threshold configurable.
```

---

## Prompt 8 — Feedback Learning

```text
Read only:
- CLAUDE.md
- .kiro/steering/product.md
- api/app/db/models.py
- api/app/services/qdrant_service.py
- api/app/services/embedding_service.py

Task: Add feedback learning.

Create/modify only:
- api/app/schemas/feedback.py
- api/app/routes/feedback.py
- api/app/services/feedback_service.py
- api/app/main.py if route registration is needed

Flow:
1. Save correction to PostgreSQL.
2. Upsert corrected answer to Qdrant with priority high.
3. Future similar questions should prefer correction memory.
```

---

## Prompt 9 — Knowledge Upload Text/Markdown

```text
Read only:
- CLAUDE.md
- .kiro/steering/clean-code.md
- api/app/services/qdrant_service.py
- api/app/services/embedding_service.py

Task: Add text/markdown knowledge ingestion.

Create/modify only:
- api/app/schemas/knowledge.py
- api/app/routes/knowledge.py
- api/app/services/document_service.py
- api/app/utils/chunk_text.py
- api/app/main.py if route registration is needed

Requirements:
- Accept text or markdown content.
- Chunk content.
- Save metadata to PostgreSQL.
- Upsert chunks to Qdrant.
- Do not support PDF yet.
```

---

## Prompt 10 — External Fallback Policy Skeleton

```text
Read only:
- CLAUDE.md
- docs/FALLBACK_POLICY.md
- api/app/services/assistant_service.py

Task: Add external fallback service skeleton only.

Create:
- api/app/services/external_fallback_service.py

Requirements:
- Disabled by default.
- Controlled by EXTERNAL_FALLBACK_ENABLED env.
- Do not call real external API yet.
- assistant_service should only call fallback if mode is external_allowed and local context is insufficient.
```

---

## Prompt 11 — Tests Minimum

```text
Read only:
- CLAUDE.md
- .kiro/steering/clean-code.md
- api/app/routes/health.py
- api/app/routes/chat.py
- api/app/services/cache_service.py

Task: Add minimum tests.

Create/modify:
- api/tests/test_health.py
- api/tests/test_chat.py
- api/tests/test_cache_service.py

Do not change production code unless test reveals a real bug.
```

---

## Prompt 12 — Final Review, No Code Change

```text
Read:
- CLAUDE.md
- docs/PRD.md
- .kiro/steering/clean-code.md

Task: Review the current implementation against the PRD.

Rules:
- Do not edit any file.
- Do not scan unrelated files.
- Return only:
  1. completed items
  2. missing items
  3. risky code areas
  4. next 5 recommended tasks
```
