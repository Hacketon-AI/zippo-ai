#!/usr/bin/env bash
# Restore zippo-ai backups made by backup.sh.
#
# Usage:
#   ./scripts/restore.sh postgres backups/postgres/zippo_20260717_031700.dump
#   ./scripts/restore.sh qdrant   backups/qdrant/memory_20260717_031700.snapshot memory
set -euo pipefail

KIND="${1:?usage: restore.sh <postgres|qdrant> <file> [collection]}"
FILE="${2:?backup file required}"

PG_CONTAINER="personal-ai-postgres"
QDRANT_URL="http://127.0.0.1:6333"

if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi

case "$KIND" in
  postgres)
    : "${POSTGRES_USER:?}"; : "${POSTGRES_DB:?}"
    echo "Restoring PostgreSQL ${POSTGRES_DB} from $FILE ..."
    docker exec -i "$PG_CONTAINER" pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
      --clean --if-exists < "$FILE"
    echo "Done."
    ;;
  qdrant)
    COLLECTION="${3:?collection name required for qdrant restore}"
    echo "Restoring Qdrant collection ${COLLECTION} from $FILE ..."
    curl -fsS -X POST "$QDRANT_URL/collections/$COLLECTION/snapshots/upload?priority=snapshot" \
      -F "snapshot=@$FILE"
    echo
    echo "Done."
    ;;
  *)
    echo "Unknown kind: $KIND (expected postgres or qdrant)" >&2
    exit 1
    ;;
esac
