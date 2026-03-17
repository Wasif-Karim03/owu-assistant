.PHONY: setup backend frontend seed dev clean

# ── Setup ────────────────────────────────────────────────────────────

setup:
	@echo "→ Copying .env.example → .env (if not exists)"
	@cp -n .env.example .env 2>/dev/null || true
	@echo "→ Starting Docker services …"
	docker-compose up -d
	@echo "→ Waiting for Postgres to be ready …"
	@sleep 3
	@echo "→ Running migrations …"
	cd backend && alembic upgrade head
	@echo "✓ Setup complete."

# ── Development ──────────────────────────────────────────────────────

backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend concurrently …"
	@(trap 'kill 0' EXIT; \
	  cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & \
	  cd frontend && npm run dev & \
	  wait)

# ── Data ─────────────────────────────────────────────────────────────

seed:
	@echo "→ Seeding manual knowledge base …"
	python ingestion/seed_manual.py
	@echo "→ Scraping OWU web pages …"
	python ingestion/seed.py
	@echo "✓ Seed complete."

seed-manual:
	python ingestion/seed_manual.py

seed-web:
	python ingestion/seed.py

# ── Tests ────────────────────────────────────────────────────────────

test:
	cd backend && python -m pytest tests/ -v

# ── Cleanup ──────────────────────────────────────────────────────────

clean:
	docker-compose down -v
	@echo "✓ Docker services stopped and volumes removed."
