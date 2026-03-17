from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.config import settings


def _build_engine_args(raw_url: str) -> tuple[str, dict]:
    """Normalise a DATABASE_URL for asyncpg.

    Neon (and many hosted Postgres providers) give URLs like
    ``postgresql://...?sslmode=require``.  asyncpg doesn't understand
    ``sslmode`` as a query-string param — it needs ``ssl`` passed via
    ``connect_args``.  This helper strips the param and returns the
    cleaned URL plus any extra ``connect_args`` needed.
    """
    url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1) \
        if raw_url.startswith("postgresql://") else raw_url

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    connect_args: dict = {}

    _STRIP_PARAMS = ("sslmode", "channel_binding")
    changed = False
    if "sslmode" in qs:
        connect_args["ssl"] = qs.pop("sslmode")[0]
        changed = True
    for param in _STRIP_PARAMS:
        if param in qs:
            qs.pop(param)
            changed = True
    if changed:
        parsed = parsed._replace(query=urlencode(qs, doseq=True))
        url = urlunparse(parsed)

    is_cloud = "localhost" not in (parsed.hostname or "") and "127.0.0.1" not in (parsed.hostname or "")
    if is_cloud and "ssl" not in connect_args:
        connect_args["ssl"] = "require"

    return url, connect_args


_url, _connect_args = _build_engine_args(settings.DATABASE_URL)

engine = create_async_engine(
    _url,
    echo=settings.ENVIRONMENT == "development",
    connect_args=_connect_args,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
