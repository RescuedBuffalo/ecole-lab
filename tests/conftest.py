import os

import asyncio
from typing import Generator

import pytest

# ensure test database URL is set before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from src.app.db import engine, Base  # noqa: E402
from src.app.main import app as fastapi_app  # noqa: E402
from src.app.math.skills import pythagorean as pyth  # noqa: E402
from src.app.math.skills.pythagorean import generate_problem  # noqa: E402


async def _setup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _teardown_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def async_db() -> Generator[None, None, None]:
    asyncio.run(_setup_db())
    yield
    asyncio.run(_teardown_db())


@pytest.fixture(scope="session")
def app(async_db: None):
    return fastapi_app


@pytest.fixture
def sample_spec() -> pyth.ProblemSpec:
    return generate_problem("pythagorean.find_c", 1)


@pytest.fixture(autouse=True)
def reset_rng() -> None:
    pyth._rng.seed(pyth.random_seed)


@pytest.fixture
def freeze_time():
    from freezegun import freeze_time as ft  # type: ignore[import-not-found]

    with ft("2024-01-01"):
        yield
