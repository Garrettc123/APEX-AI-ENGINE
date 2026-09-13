"""Database initialization and session management"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from apex.config import settings
from apex.db.models import Base
import structlog

log = structlog.get_logger()


def _async_database_url(url: str) -> str:
    if url.startswith("sqlite+aiosqlite://"):
        return url
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


_url = _async_database_url(settings.DATABASE_URL)
_connect_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}
# Local compose often runs nested; avoid SSL negotiation hangs on Postgres.
_engine_kwargs = {"echo": settings.DEBUG}
if _url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = _connect_args
else:
    _engine_kwargs.update(pool_size=5, max_overflow=10, pool_pre_ping=True)
    _engine_kwargs["connect_args"] = {"ssl": False, "timeout": 5}

engine = create_async_engine(_url, **_engine_kwargs)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("db.initialized", url=_url.split("@")[-1] if "@" in _url else _url)
    except Exception as exc:
        log.error("db.init_failed", error=str(exc))
        raise


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
