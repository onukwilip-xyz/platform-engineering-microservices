import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# PGBouncer transaction-mode compatibility settings only apply to Postgres.
# SQLite (used in tests/local) doesn't support these kwargs.
is_postgres = DATABASE_URL.startswith("postgresql")

engine_kwargs = {
    "future": True,
    "echo": False,  # flip to True only when debugging; very noisy under load
}

if is_postgres:
    engine_kwargs.update({
    "pool_pre_ping": True,
    "pool_recycle": 1800,
    "pool_size": 25,                  
    "max_overflow": 50,
    "pool_timeout": 10,

    "connect_args": {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
})

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()