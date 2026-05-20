# PRD — Personal AI Assistant Lokal Berbasis Qwen3, Ollama, FastAPI, Docker, PostgreSQL, dan Qdrant

## 1. Ringkasan Produk

Personal AI Assistant adalah sistem asisten AI pribadi yang berjalan di VPS pribadi menggunakan Docker. Sistem ini menggunakan Qwen3 melalui Ollama sebagai model AI lokal, FastAPI sebagai backend, PostgreSQL sebagai penyimpanan cache/history/feedback, dan Qdrant sebagai vector database untuk memori semantik/RAG.

Tujuan utama sistem adalah membuat AI pribadi yang bisa membantu pekerjaan harian seperti coding, dokumentasi, analisis bug, membuat laporan PM, membaca dokumen project, menyimpan knowledge, dan hanya menggunakan API eksternal jika data lokal tidak cukup.

Sistem dirancang untuk berjalan pada VPS kecil seperti Hostinger KVM 2, sehingga harus ringan, modular, aman, dan hemat resource.

---

## 2. Masalah yang Ingin Diselesaikan

### 2.1 Masalah Utama

Saat menggunakan AI berbasis API, beberapa masalah sering muncul:

- Boros token/kredit.
- AI tidak ingat konteks project pribadi.
- Harus mengulang penjelasan yang sama berkali-kali.
- Data pribadi/project dikirim ke layanan luar.
- Tidak ada sistem cache untuk jawaban yang sudah pernah dicari.
- Tidak ada memori permanen berbasis dokumen dan koreksi user.

### 2.2 Solusi

Bangun AI pribadi lokal dengan konsep:

```text
Local-first AI Assistant
↓
Cek cache PostgreSQL
↓
Cek semantic memory Qdrant
↓
Cek knowledge base lokal
↓
Jawab dengan Qwen3 lokal
↓
Fallback ke API eksternal hanya jika diperlukan
↓
Simpan hasil baru ke database agar tidak request ulang
```

---

## 3. Tujuan Produk

### 3.1 Tujuan Bisnis/Personal

- Memiliki AI pribadi yang bisa berjalan di VPS sendiri.
- Menghemat penggunaan API eksternal seperti Claude/Groq/OpenAI.
- Membuat AI bisa memahami project pribadi, dokumentasi, catatan bug, dan SOP.
- Membuat AI bisa belajar dari koreksi user tanpa fine-tuning mahal.
- Menjadi fondasi untuk integrasi ke project lain, seperti backend, koperasi, aplikasi internal, atau asisten coding.

### 3.2 Tujuan Teknis

- Backend menggunakan Python FastAPI.
- Semua service berjalan via Docker Compose.
- Model utama menggunakan Ollama + Qwen3.
- PostgreSQL digunakan untuk cache, conversation, feedback, dan metadata.
- Qdrant digunakan untuk semantic memory dan RAG.
- Struktur code clean, modular, dan testable.
- API eksternal hanya digunakan sebagai fallback.
- Security minimal production-ready untuk VPS pribadi.

---

## 4. Target User

### 4.1 Primary User

Pemilik sistem/asisten pribadi.

Kebutuhan:

- Tanya jawab harian.
- Bantu coding.
- Bantu refactor.
- Bantu membaca dokumentasi.
- Bantu membuat laporan teknis.
- Bantu menganalisis bug.
- Bantu menyimpan knowledge penting.

### 4.2 Future User

- Tim kecil developer.
- Admin internal.
- Customer support internal.
- Sistem koperasi/internal tools.

---

## 5. Scope MVP

### 5.1 Fitur MVP Wajib

1. FastAPI backend skeleton.
2. Docker Compose untuk semua service.
3. Ollama service dengan Qwen3.
4. Open WebUI untuk chat UI opsional.
5. PostgreSQL untuk cache dan history.
6. Qdrant untuk vector memory.
7. Endpoint `/health`.
8. Endpoint `/chat`.
9. Exact cache dari PostgreSQL.
10. Semantic search dari Qdrant.
11. Knowledge ingestion sederhana.
12. Feedback learning.
13. Environment configuration via `.env`.
14. Logging basic.
15. API fallback policy, tapi implementasi fallback eksternal boleh tahap lanjutan.

### 5.2 Fitur Bukan MVP

- Fine-tuning model.
- Multi-user permission kompleks.
- Payment/subscription.
- Frontend custom besar.
- Agent automation kompleks.
- Integrasi WhatsApp/Telegram.
- Full observability stack.

---

## 6. Tech Stack

### 6.1 Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Alembic
- httpx
- python-dotenv / pydantic-settings

### 6.2 AI Runtime

- Ollama
- Qwen3 sebagai model utama
- Model default untuk VPS kecil: `qwen3:4b`
- Optional jika RAM cukup: `qwen3:8b`
- Embedding model: `nomic-embed-text` atau `bge-m3`

### 6.3 Database

- PostgreSQL untuk structured data.
- Qdrant untuk vector database.

### 6.4 Infrastructure

- Docker Compose
- Nginx reverse proxy
- UFW firewall
- SSL via Let's Encrypt atau Cloudflare

---

## 7. Arsitektur Sistem

```text
User / Open WebUI / Custom Client
        ↓
FastAPI AI Gateway
        ↓
Assistant Service
        ↓
┌───────────────────────────────────────────┐
│ 1. Normalize question                     │
│ 2. Check correction memory                │
│ 3. Check PostgreSQL exact cache           │
│ 4. Check Qdrant semantic memory           │
│ 5. Build prompt with context              │
│ 6. Call Qwen3 via Ollama                  │
│ 7. Validate answer                        │
│ 8. Save answer to PostgreSQL + Qdrant     │
└───────────────────────────────────────────┘
        ↓
Optional External API Fallback
```

---

## 8. Struktur Folder Wajib

```text
personal-ai-assistant/
├── README.md
├── CLAUDE.md
├── docker-compose.yml
├── .env.example
├── Makefile
├── .kiro/
│   └── steering/
│       ├── product.md
│       ├── structure.md
│       ├── tech.md
│       ├── clean-code.md
│       └── token-saving.md
├── docs/
│   ├── PRD.md
│   ├── API_SPEC.md
│   ├── MIGRATION_PLAN.md
│   ├── FALLBACK_POLICY.md
│   └── DEPLOYMENT.md
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   ├── knowledge.py
│   │   │   └── feedback.py
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── chat.py
│   │   │   ├── knowledge.py
│   │   │   └── feedback.py
│   │   ├── services/
│   │   │   ├── assistant_service.py
│   │   │   ├── ollama_service.py
│   │   │   ├── cache_service.py
│   │   │   ├── qdrant_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── memory_service.py
│   │   │   ├── document_service.py
│   │   │   ├── feedback_service.py
│   │   │   └── external_fallback_service.py
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   ├── rag_prompt.md
│   │   │   └── coding_prompt.md
│   │   └── utils/
│   │       ├── text_normalizer.py
│   │       ├── chunk_text.py
│   │       └── ttl_policy.py
│   └── tests/
│       ├── test_health.py
│       ├── test_chat.py
│       ├── test_cache_service.py
│       └── test_memory_service.py
├── data/
│   ├── uploads/
│   ├── backups/
│   └── exports/
└── scripts/
    ├── backup.sh
    ├── restore.sh
    └── ingest_docs.py
```

---

## 9. Database Design

### 9.1 Tabel `conversation_sessions`

Menyimpan sesi percakapan.

Fields:

- `id`
- `title`
- `created_at`
- `updated_at`

### 9.2 Tabel `chat_messages`

Menyimpan riwayat pesan.

Fields:

- `id`
- `session_id`
- `role` — user/assistant/system
- `content`
- `metadata`
- `created_at`

### 9.3 Tabel `ai_cache`

Menyimpan exact cache.

Fields:

- `id`
- `question_hash`
- `normalized_question`
- `answer`
- `source_type`
- `source_refs`
- `confidence_score`
- `expires_at`
- `created_at`
- `updated_at`

### 9.4 Tabel `knowledge_documents`

Menyimpan metadata dokumen.

Fields:

- `id`
- `title`
- `file_name`
- `file_path`
- `source_type`
- `tags`
- `created_at`
- `updated_at`

### 9.5 Tabel `feedback_corrections`

Menyimpan koreksi user.

Fields:

- `id`
- `question`
- `wrong_answer`
- `corrected_answer`
- `category`
- `priority`
- `created_at`

---

## 10. Qdrant Collection Design

### 10.1 Collection: `personal_ai_memory`

Digunakan untuk:

- Knowledge base.
- Corrected answers.
- Ringkasan dokumen.
- Cache semantic.

Payload metadata:

```json
{
  "type": "knowledge|cache|correction|document",
  "title": "string",
  "source": "string",
  "category": "string",
  "priority": "low|normal|high",
  "created_at": "datetime",
  "expires_at": "datetime|null"
}
```

---

## 11. Chat Flow

### 11.1 Normal Flow

```text
POST /api/v1/chat
↓
Validate request
↓
Normalize question
↓
Check correction memory
↓
Check exact cache PostgreSQL
↓
Check Qdrant semantic memory
↓
If context found: build RAG prompt
↓
Call Ollama Qwen3
↓
Return answer
↓
Save message history
↓
Save answer to cache/vector DB if useful
```

### 11.2 Fallback Flow

External API hanya boleh dipakai jika:

- Cache tidak ada.
- Qdrant score rendah.
- Pertanyaan butuh data terbaru.
- Qwen lokal gagal menjawab.
- User secara eksplisit meminta data terbaru/API eksternal.

---

## 12. Endpoint API

### 12.1 Health

`GET /api/v1/health`

Response:

```json
{
  "status": "ok",
  "service": "personal-ai-assistant"
}
```

### 12.2 Chat

`POST /api/v1/chat`

Request:

```json
{
  "message": "string",
  "session_id": "optional",
  "mode": "auto|local_only|external_allowed",
  "use_memory": true
}
```

Response:

```json
{
  "answer": "string",
  "source": "cache|memory|ollama|external",
  "session_id": "string",
  "metadata": {
    "model": "qwen3:4b",
    "used_context": true,
    "similarity_score": 0.82
  }
}
```

### 12.3 Knowledge Upload

`POST /api/v1/knowledge/upload`

Fungsi:

- Upload dokumen text/markdown/pdf tahap lanjutan.
- Chunk dokumen.
- Generate embedding.
- Simpan metadata ke PostgreSQL.
- Simpan vector ke Qdrant.

### 12.4 Feedback

`POST /api/v1/feedback`

Request:

```json
{
  "question": "string",
  "wrong_answer": "string",
  "corrected_answer": "string",
  "category": "optional"
}
```

Response:

```json
{
  "status": "saved",
  "message": "Correction saved to memory"
}
```

---

## 13. Clean Code Requirement

### 13.1 Rules

- Routes harus tipis, tidak berisi business logic.
- Business logic wajib di services.
- Prompt template wajib dipisah di folder prompts.
- Config wajib dari environment variable.
- Tidak boleh hardcode secret.
- Gunakan type hints.
- Gunakan Pydantic schema untuk request/response.
- Gunakan exception handling yang jelas.
- Setiap service penting harus mudah di-test.
- Jangan membuat dependency yang tidak perlu.
- Jangan langsung implement fitur besar tanpa phase.

### 13.2 Layer Responsibility

- `routes/`: HTTP request/response only.
- `schemas/`: Pydantic DTO.
- `services/`: business rules.
- `db/`: database model/session.
- `prompts/`: prompt templates.
- `utils/`: helper kecil tanpa dependency berat.

---

## 14. Security Requirement

- Jangan expose port Ollama ke publik.
- Jangan commit `.env`.
- Gunakan `.env.example`.
- Gunakan firewall VPS.
- Gunakan Nginx reverse proxy.
- Gunakan SSL.
- Batasi upload file size.
- Sanitasi file upload.
- Jangan log API key.
- Jangan log dokumen sensitif secara penuh.

---

## 15. Performance Requirement untuk VPS Kecil

Karena VPS target adalah kelas kecil, sistem wajib:

- Default model: `qwen3:4b`.
- Jangan langsung load model besar.
- Gunakan cache PostgreSQL.
- Gunakan Qdrant search limit kecil, misalnya 5.
- Batasi chunk size dokumen.
- Batasi max token output default.
- Gunakan external API hanya fallback.
- Tambahkan swap memory jika VPS RAM terbatas.

---

## 16. Token Saving Strategy untuk Development di Kiro

Karena kredit terbatas sampai reset 1 Juni 2026, development harus hemat.

Rules:

- Jangan minta Kiro membaca seluruh repo.
- Satu task maksimal 3–5 file.
- Satu prompt untuk satu tujuan kecil.
- Minta Kiro list file yang akan diubah sebelum edit.
- Jangan generate ulang file yang sudah jadi.
- Jangan minta penjelasan panjang jika tidak perlu.
- Simpan semua aturan di CLAUDE.md dan `.kiro/steering`.
- Gunakan Opus hanya untuk planning/review penting.
- Implementasi kecil bisa pakai model lebih murah jika tersedia.

---

## 17. Kiro Steering Files yang Wajib Dibuat

Kiro steering harus dibuat di:

```text
.kiro/steering/
├── product.md
├── structure.md
├── tech.md
├── clean-code.md
└── token-saving.md
```

Isi detail masing-masing file ada di paket project ini.

---

## 18. Development Phases

### Phase 0 — Project Preparation

Output:

- Repo baru.
- `CLAUDE.md`.
- `.kiro/steering/*`.
- `docs/PRD.md`.
- `.env.example`.

### Phase 1 — Backend Skeleton

Output:

- FastAPI app.
- Health endpoint.
- Docker Compose basic.
- PostgreSQL service.
- Qdrant service.
- Ollama service.

### Phase 2 — Ollama Integration

Output:

- `ollama_service.py`.
- Config model dari env.
- Chat endpoint basic.

### Phase 3 — PostgreSQL Cache

Output:

- Cache table.
- Cache service.
- Chat flow pakai exact cache.

### Phase 4 — Qdrant Memory

Output:

- Embedding service.
- Qdrant service.
- Semantic search.
- Save semantic memory.

### Phase 5 — Knowledge Ingestion

Output:

- Upload text/markdown.
- Chunking.
- Embedding.
- Upsert to Qdrant.

### Phase 6 — Feedback Learning

Output:

- Feedback endpoint.
- Correction memory.
- Correction priority di flow chat.

### Phase 7 — External Fallback Optional

Output:

- Groq/Claude/OpenRouter fallback config.
- Policy agar tidak boros API.
- Save external answer to cache.

### Phase 8 — Deployment Hardening

Output:

- Nginx config.
- SSL.
- Firewall.
- Backup script.
- Monitoring ringan.

---

## 19. Acceptance Criteria

MVP dianggap selesai jika:

- `docker compose up -d` berhasil menjalankan service utama.
- `/api/v1/health` return OK.
- `/api/v1/chat` bisa menjawab via Qwen3 lokal.
- Jawaban yang sama bisa diambil dari PostgreSQL cache.
- Pertanyaan mirip bisa mengambil context dari Qdrant.
- User bisa menyimpan koreksi via `/feedback`.
- Koreksi user diprioritaskan pada jawaban berikutnya.
- Ollama tidak expose publik.
- Semua secret via `.env`.
- Struktur code mengikuti clean architecture.

---

## 20. Definition of Done

Setiap phase dianggap selesai jika:

- Code berjalan.
- Tidak ada secret hardcoded.
- Minimal ada test untuk service utama.
- Dokumentasi kecil diperbarui.
- Docker masih bisa jalan.
- Tidak ada perubahan file di luar scope task.
- Kiro/Claude memberikan ringkasan diff.

