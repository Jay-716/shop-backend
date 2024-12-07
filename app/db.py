from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from redis import Redis

from config import user, password, host, db_name, redis_host, redis_port

DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
DATABASE_URL_ASYNC = f"mysql+aiomysql://{user}:{password}@{host}/{db_name}"
REDIS_HOST = redis_host
REDIS_PORT = redis_port


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
async_engine = create_async_engine(DATABASE_URL_ASYNC, pool_pre_ping=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_redis() -> Generator[Redis, None, None]:
    with Redis(host=REDIS_HOST, port=REDIS_PORT) as r:
        yield r
