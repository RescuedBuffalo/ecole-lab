from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context

from ..db import Base, engine
import src.app.models  # noqa: F401

config = context.config
fileConfig(config.config_file_name)  # type: ignore[arg-type]
target_metadata = Base.metadata


def run_migrations_online() -> None:
    async def do_migrations() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(do_migrations())


def run_migrations_offline() -> None:
    run_migrations_online()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
