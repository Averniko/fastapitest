from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import DATABASE_URL, SHOW_DB_LOG
from crud import UserDatabase
from models import Base, User

engine = create_async_engine(DATABASE_URL, echo=SHOW_DB_LOG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield UserDatabase(session, User)
