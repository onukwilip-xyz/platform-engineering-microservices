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
        # Test connections with a lightweight SELECT 1 before handing them out.
        # Fixes "connection is closed" errors when PGBouncer recycles a backend
        # but SQLAlchemy's pool still thinks the connection is alive.
        "pool_pre_ping": True,

        # Recycle connections older than 30 min to avoid stale ones surviving
        # PGBouncer's server_idle_timeout or network idle timeouts.
        "pool_recycle": 1800,

        # SQLAlchemy's own pool sizing. With PGBouncer in front, keep these
        # modest — PGBouncer is doing the real multiplexing. Each replica of
        # the users service holds up to (pool_size + max_overflow) connections
        # open to PGBouncer.
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,

        # Critical for PGBouncer TRANSACTION mode:
        # - asyncpg's prepared-statement cache assumes a sticky backend.
        #   PGBouncer routes each transaction to whichever backend is free,
        #   so cached prepared statements end up on the wrong backend and
        #   fail with DuplicatePreparedStatementError or silently misbehave.
        # - statement_cache_size=0 disables asyncpg's server-side prepared stmts
        # - prepared_statement_cache_size=0 disables the client-side cache too
        "connect_args": {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
            "server_settings": {
                # Disable JIT — it gives unpredictable latency under load and
                # the planning overhead rarely helps for short OLTP queries.
                "jit": "off",
            },
        },
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()