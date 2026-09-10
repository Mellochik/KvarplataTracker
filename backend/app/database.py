import os
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_DB_PATH = _BACKEND_DIR.parent / "data" / "kvarplata.db"

DATABASE_URL = (
    os.getenv("DATABASE_URL") or f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH.as_posix()}"
)

if not os.environ.get("DATABASE_URL"):
    _DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
