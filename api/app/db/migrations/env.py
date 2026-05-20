"""Alembic environment configuration.

Loads DATABASE_URL from the environment (or app settings as fallback)
and supports both online (async) and offline migration modes.
"""

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Make `app.*` importable when Alembic runs from the repo root.
# This file lives at: <repo>/api/app/db/migrations/env.py
# Adding <repo>/api to sys.path exposes the `app` package.
_API_DIR = Path(__file__).resolve().parents[3]
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from app.db.models import Base  # noqa: E402

# Alembic Config object.
config = context.config

# Configure logging from alembic.ini if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_database_url() -> str:
    """Resolve the database URL from env or app settings."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Fallback to application settings (no DB connection is opened here).
    from app.core.config import get_settings

    return get_settings().database_url


# Inject the URL into the Alembic config so engine_from_config picks it up.
config.set_main_option("sqlalchemy.url", _get_database_url())

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without a DB connection)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online_async() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_migrations_online_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
