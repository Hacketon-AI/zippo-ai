#!/usr/bin/env bash
# Daily backup for zippo-ai: PostgreSQL dump + Qdrant snapshots.
# Backups land OUTSIDE Docker volumes so a wrong `docker volume rm`
# can no longer destroy them.
#
# Usage:
#   ./scripts/backup.sh [backup_dir]     # default: ./backups
#
# Cron example (daily at 03:17):
#   17 3 * * * cd /path/to/zippo-ai && ./scripts/backup.sh >> backups/backup.log 2>&1
set -euo pipefail

BACKUP_DIR="${1:-$(pwd)/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
STAMP="$(date +%Y%m%d_%H%M%S)"

PG_CONTAINER="personal-ai-postgres"
QDRANT_URL="http://127.0.0.1:6333"

mkdir -p "$BACKUP_DIR/postgres" "$BACKUP_DIR/qdrant"

# Load POSTGRES_* from .env (never hardcode credentials here).
if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi
: "${POSTGRES_USER:?POSTGRES_USER not set (missing .env?)}"
: "${POSTGRES_DB:?POSTGRES_DB not set (missing .env?)}"

echo "[$STAMP] Backing up PostgreSQL (${POSTGRES_DB})..."
docker exec "$PG_CONTAINER" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
  > "$BACKUP_DIR/postgres/${POSTGRES_DB}_${STAMP}.dump"

echo "[$STAMP] Backing up Qdrant collections..."
collections=$(curl -fsS "$QDRANT_URL/collections" | python3 -c \
  'import sys,json; print("\n".join(c["name"] for c in json.load(sys.stdin)["result"]["collections"]))')

for col in $collections; do
  snap=$(curl -fsS -X POST "$QDRANT_URL/collections/$col/snapshots" | python3 -c \
    'import sys,json; print(json.load(sys.stdin)["result"]["name"])')
  curl -fsS "$QDRANT_URL/collections/$col/snapshots/$snap" \
    -o "$BACKUP_DIR/qdrant/${col}_${STAMP}.snapshot"
  # Remove server-side snapshot so the qdrant volume doesn't grow.
  curl -fsS -X DELETE "$QDRANT_URL/collections/$col/snapshots/$snap" > /dev/null
  echo "  - $col -> ${col}_${STAMP}.snapshot"
done

echo "[$STAMP] Pruning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR/postgres" -name '*.dump' -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR/qdrant" -name '*.snapshot' -mtime +"$RETENTION_DAYS" -delete

echo "[$STAMP] Done. Backups in $BACKUP_DIR"
