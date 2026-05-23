from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("sqlite+aiosqlite://"):
        return raw_url

    normalized = raw_url
    if raw_url.startswith("postgresql+asyncpg://"):
        normalized = raw_url
    elif raw_url.startswith("postgres://"):
        normalized = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif raw_url.startswith("postgresql://"):
        normalized = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif raw_url.startswith("postgresql+psycopg://"):
        normalized = raw_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    if not normalized.startswith("postgresql+asyncpg://"):
        return normalized

    parts = urlsplit(normalized)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    sslmode = query.pop("sslmode", None)
    if sslmode and "ssl" not in query:
        query["ssl"] = "require" if sslmode == "require" else sslmode

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )


DATABASE_URL = _normalize_database_url(settings.database_url)
IS_SQLITE = DATABASE_URL.startswith("sqlite+aiosqlite://")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=not IS_SQLITE,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def create_tables():
    from app.models.user import User  # noqa
    from app.models.financial_profile import FinancialProfile  # noqa
    from app.models.recommendation import Recommendation  # noqa
    from app.models.simulation import Simulation  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_financial_profile_columns)


def _ensure_financial_profile_columns(sync_conn) -> None:
    inspector = inspect(sync_conn)
    if "financial_profiles" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("financial_profiles")}
    if "monthly_debt_obligations" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE financial_profiles ADD COLUMN monthly_debt_obligations FLOAT NOT NULL DEFAULT 0.0"
        )
    if "age" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE financial_profiles ADD COLUMN age INTEGER"
        )
    if "credit_gender" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE financial_profiles ADD COLUMN credit_gender VARCHAR(16)"
        )
    if "emergency_fund" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE financial_profiles ADD COLUMN emergency_fund FLOAT NOT NULL DEFAULT 0.0"
        )


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
