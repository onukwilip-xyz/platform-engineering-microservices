import os

from fastapi import FastAPI
import uvicorn

from db.config import engine, Base
from routers import user_router
from fastapi import Depends
from db.config import async_session
from db.models.user import User

app = FastAPI()
app.include_router(user_router.router)


@app.on_event("startup")
async def startup():
    # Non-destructive by default: create missing tables only. When
    # SEED_ON_STARTUP=true, drop + recreate + reseed the three demo users —
    # safe for local/dev, never enable in prod.
    async with engine.begin() as conn:
        if os.getenv("SEED_ON_STARTUP", "false").lower() == "true":
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    if os.getenv("SEED_ON_STARTUP", "false").lower() == "true":
        async with async_session() as session:
            async with session.begin():
                session.add_all([
                    User(name='Peter', email='peter@exmaple.com', mobile='298479284'),
                    User(name='John', email='john@exmaple.com', mobile='998479284'),
                    User(name='Jason', email='jason@exmaple.com', mobile='928479285'),
                ])
            await session.commit()


if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "9090")),
        log_level=os.getenv("LOG_LEVEL", "info"),
    )