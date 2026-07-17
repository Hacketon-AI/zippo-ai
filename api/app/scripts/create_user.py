"""Seed a user account (no signup flow exists yet).

Usage:
    python -m app.scripts.create_user email@example.com password "Display Name"

Running twice with the same email updates the password and display name.
"""

from __future__ import annotations

import asyncio
import sys

from sqlalchemy import select

from app.db.models import User
from app.db.session import dispose_engine, get_session_factory
from app.services.auth_service import hash_password


async def _create_user(email: str, password: str, display_name: str) -> str:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(User).where(User.email == email).limit(1)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if user is None:
            session.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    display_name=display_name,
                )
            )
            action = "created"
        else:
            user.password_hash = hash_password(password)
            user.display_name = display_name
            action = "updated"
        await session.commit()
    await dispose_engine()
    return action


def main() -> None:
    if len(sys.argv) != 4:
        print(
            'Usage: python -m app.scripts.create_user '
            '<email> <password> "<display name>"',
            file=sys.stderr,
        )
        raise SystemExit(2)

    email = sys.argv[1].strip().lower()
    password = sys.argv[2]
    display_name = sys.argv[3].strip()

    if "@" not in email or not password or not display_name:
        print("Invalid email, empty password, or empty name", file=sys.stderr)
        raise SystemExit(2)

    action = asyncio.run(_create_user(email, password, display_name))
    print(f"User {email} {action}.")


if __name__ == "__main__":
    main()
