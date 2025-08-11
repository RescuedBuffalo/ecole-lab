from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, future=True)
async_session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[call-overload]
