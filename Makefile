.PHONY: help up down restart build logs ps health env db-revision db-migrate db-downgrade

help:
	@echo "Targets:"
	@echo "  env           - copy .env.example to .env if missing"
	@echo "  build         - build api image"
	@echo "  up            - start all services in background"
	@echo "  down          - stop all services"
	@echo "  restart       - restart all services"
	@echo "  logs          - follow logs for all services"
	@echo "  ps            - list running containers"
	@echo "  health        - curl the health endpoint"
	@echo "  db-revision   - autogenerate a new Alembic revision (M=\"message\")"
	@echo "  db-migrate    - apply Alembic migrations to head"
	@echo "  db-downgrade  - downgrade one revision (REV=-1 to override)"

env:
	@test -f .env || cp .env.example .env

build:
	docker compose build

up: env
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

health:
	curl -fsS http://localhost:8000/api/v1/health

# ----- Alembic migrations (run inside a one-off api container) -----
# Bind-mounts the repo so alembic.ini and migrations are visible.
# Usage:
#   make db-revision M="create initial tables"
#   make db-migrate
#   make db-downgrade            # one step
#   make db-downgrade REV=base   # override target
M ?= update schema
REV ?= -1

ALEMBIC_RUN = docker compose run --rm \
	-v "$(PWD)":/workspace \
	-w /workspace \
	api alembic

db-revision:
	$(ALEMBIC_RUN) revision --autogenerate -m "$(M)"

db-migrate:
	$(ALEMBIC_RUN) upgrade head

db-downgrade:
	$(ALEMBIC_RUN) downgrade $(REV)
