from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./ecole.db"
    outbox_dir: str = "outbox"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
