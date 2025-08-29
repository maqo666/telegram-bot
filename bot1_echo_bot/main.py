import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiogram.filters import CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database import create_db_and_tables, get_db
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import router as admin_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def session_middleware(handler, event, data):
    """Middleware для предоставления сессии БД"""
    async for session in get_db():
        data["session"] = session
        return await handler(event, data)

async def main():
    # Создаем таблицы в БД
    await create_db_and_tables()
    logger.info("Database tables created")
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Добавляем middleware для работы с БД
    dp.update.middleware(session_middleware)
    
    # Подключаем роутеры
    dp.include_router(user_router)
    dp.include_router(admin_router)
    
    # Запускаем поллинг
    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")