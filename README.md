# OWU Campus Assistant

A RAG-powered chatbot that answers Ohio Wesleyan University student questions using real university content. Built with **FastAPI**, **Next.js 14**, **pgvector**, and **Claude**.

Students can ask about campus offices, events, deadlines, financial aid, academic resources, and more — and get accurate, citation-backed answers drawn from official OWU data.

---

## 5-Minute Quickstart

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| Docker & Docker Compose | Latest |

### 1. Clone and configure

```bash
git clone <repo-url>
cd owu-assistant
cp .env.example .env
```

Open `.env` and add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 2. Start Postgres

```bash
docker-compose up -d
```

This starts PostgreSQL 16 with the pgvector extension on port 5432.

### 3. Run database migrations

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
cd ..
```

### 4. Seed the knowledge base

```bash
python ingestion/seed_manual.py    # office info (instant, no API calls needed for scraping)
python ingestion/seed.py           # scrape OWU website pages (needs OPENAI_API_KEY for embeddings)
```

### 5. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** — you should see the OWU Assistant chat UI.

### Or use Make

```bash
make setup    # .env + docker + migrations
make seed     # seed manual + web content
make dev      # start backend + frontend concurrently
```

---

## How the RAG Pipeline Works

```
Student question
       │
       ▼
┌──────────────┐     ┌───────────────────┐
│  Embed query │────▶│  pgvector cosine  │
│  (OpenAI)    │     │  similarity search│
└──────────────┘     └───────┬───────────┘
                             │
                     top-k relevant chunks
                             │
                             ▼
                   ┌─────────────────┐
                   │ Build prompt:   │
                   │ system rules +  │
                   │ context chunks +│
                   │ chat history +  │
                   │ student question│
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Claude API     │
                   │  (Anthropic)    │
                   └────────┬────────┘
                            │
                            ▼
                   Answer with source citations
```

1. **Ingestion** — Documents (web pages, emails, manual entries) are chunked into ~800-character segments, embedded with OpenAI `text-embedding-3-small`, and stored in pgvector.
2. **Retrieval** — The student's question is embedded and compared against all chunks via cosine similarity. The top 6 chunks above a 0.35 threshold are returned.
3. **Generation** — A system prompt with strict grounding rules, conversation history, and the retrieved context are sent to Claude. The model answers using only the provided context and cites its sources.

---

## Adding New Content

### Option A: Admin Panel (web UI)

Visit **http://localhost:3000/admin** to:

- **Ingest a URL** — paste any OWU webpage URL and click "Ingest"
- **Add OWU Daily Email** — paste the email body, set the date, click "Ingest Email"

### Option B: CLI scripts

```bash
# Ingest a single URL
python ingestion/seed.py --url https://www.owu.edu/some-page/

# Ingest an email from a file
python ingestion/add_email.py --file path/to/email.txt --date 2025-03-15

# Re-scrape all default OWU pages
python ingestion/seed.py
```

### Option C: Update manual office information

Edit `backend/app/ingestion/manual_entries.py` and update the `MANUAL_KNOWLEDGE_BASE` list. Then re-run:

```bash
python ingestion/seed_manual.py
```

This is idempotent — existing entries are updated, not duplicated.

---

## Project Structure

```
owu-assistant/
├── frontend/                   # Next.js 14 (App Router, Tailwind, TypeScript)
│   ├── app/
│   │   ├── page.tsx            # Main chat interface
│   │   ├── admin/page.tsx      # Admin panel for content ingestion
│   │   └── not-found.tsx       # 404 page
│   ├── components/             # ChatMessage, ChatInput, WelcomeBanner, etc.
│   └── lib/                    # API client, session management
│
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── main.py             # App entry point, CORS, lifespan
│   │   ├── config.py           # Pydantic settings from .env
│   │   ├── database.py         # Async SQLAlchemy + pgvector
│   │   ├── models.py           # Document, DocumentChunk, Conversation, Message
│   │   ├── rag/                # Retriever, prompt builder, chat engine
│   │   ├── routers/            # /api/chat, /api/admin, /api/health
│   │   └── ingestion/          # Chunker, embedder, web scraper, email parser, pipeline
│   ├── alembic/                # Database migrations
│   └── tests/                  # Pytest test suite
│
├── ingestion/                  # Standalone CLI scripts for seeding data
│   ├── seed.py                 # Scrape OWU web pages
│   ├── seed_manual.py          # Seed hardcoded office info
│   └── add_email.py            # Ingest an OWU Daily email
│
├── docker-compose.yml          # Postgres (pgvector) + backend
├── Makefile                    # Developer convenience commands
├── .env.example                # Environment variable template
└── .gitignore
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Yes |
| `DATABASE_URL` | PostgreSQL connection string (async driver) | Yes |
| `POSTGRES_USER` | Postgres user (for Docker) | For Docker |
| `POSTGRES_PASSWORD` | Postgres password (for Docker) | For Docker |
| `POSTGRES_DB` | Database name (for Docker) | For Docker |
| `FRONTEND_URL` | Frontend origin for CORS | Yes |
| `ENVIRONMENT` | `development` or `production` | No (default: development) |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service status |
| `GET` | `/api/health` | DB + Claude API health check |
| `POST` | `/api/chat/message` | Send a chat message |
| `GET` | `/api/chat/history/{session_id}` | Get conversation history |
| `DELETE` | `/api/chat/history/{session_id}` | Clear a conversation |
| `POST` | `/api/admin/ingest/url` | Ingest a web page |
| `POST` | `/api/admin/ingest/email` | Ingest an OWU Daily email |
| `GET` | `/api/admin/stats` | Document/chunk counts |

---

## Testing

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Deployment

| Component | Recommended Platform |
|-----------|---------------------|
| Frontend | **Vercel** — connect the `frontend/` directory, set `NEXT_PUBLIC_API_URL` |
| Backend | **Railway** or **Render** — deploy the `backend/` directory with the Dockerfile |
| Database | **Supabase** (pgvector supported) or **Railway Postgres** |

For production, set `ENVIRONMENT=production` to enable the automatic 24-hour content refresh scheduler and disable SQL echo logging.
