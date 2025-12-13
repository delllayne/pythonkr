# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session