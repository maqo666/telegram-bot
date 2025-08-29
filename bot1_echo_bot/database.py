from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import config

class Base(DeclarativeBase):
    pass

# Создаем движок для работы с БД
engine = create_async_engine(config.DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    """Создает все таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Генератор сессий для dependency injection"""
    async with async_session_maker() as session:
        yield session