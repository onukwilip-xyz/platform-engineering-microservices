
from db.config import async_session
from db.dals.user_dal import UserDAL


async def get_user_dal():
    """
    IMPORTANT: Do NOT use `async with session.begin():` here.
    That pattern holds the DB connection through FastAPI response serialization,
    causing deadlocks under load with PGBouncer in transaction mode.
    Always commit/rollback explicitly so connections return to the pool ASAP.
    """
    async with async_session() as session:
        try:
            yield UserDAL(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise