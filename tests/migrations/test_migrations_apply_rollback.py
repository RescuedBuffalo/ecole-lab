import asyncio
import sqlalchemy as sa

from src.app.db import engine, Base


async def _setup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _teardown_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def test_migrations_upgrade_and_rollback():
    async def run() -> None:
        await _setup_db()
        async with engine.begin() as conn:
            tables = await conn.run_sync(lambda c: sa.inspect(c).get_table_names())
            assert "participants" in tables
        await _teardown_db()
        async with engine.begin() as conn:
            tables = await conn.run_sync(lambda c: sa.inspect(c).get_table_names())
            assert "participants" not in tables

    asyncio.run(run())
