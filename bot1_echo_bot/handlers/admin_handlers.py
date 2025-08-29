from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, func
from datetime import datetime

from database import get_db
from config import config
from keyboards.inline_kb import get_admin_keyboard
from models.user import User

router = Router()

# Фильтр для проверки админа
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к админ-панели.")
        return
    
    await message.answer(
        "👨‍💻 Панель администратора:",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Показать статистику бота"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав доступа", show_alert=True)
        return
    
    try:
        async for session in get_db():
            # Получаем общее количество пользователей
            total_users_stmt = select(func.count(User.user_id))
            result = await session.execute(total_users_stmt)
            total_users = result.scalar()
            
            # Получаем количество новых пользователей за сегодня
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_users_today_stmt = select(func.count(User.user_id)).where(User.created_at >= today_start)
            result_today = await session.execute(new_users_today_stmt)
            new_users_today = result_today.scalar()
            
            stats_text = (
                f"📊 Статистика бота:\n"
                f"👥 Всего пользователей: {total_users}\n"
                f"🆕 Новых за сегодня: {new_users_today}\n"
                f"👑 Админов: {len(config.ADMIN_IDS)}"
            )
            
            await callback.message.edit_text(stats_text)
        
    except Exception as e:
        error_text = f"❌ Ошибка при получении статистики: {str(e)}"
        await callback.message.edit_text(error_text)
    
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):
    """Обработчик рассылки (заглушка)"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав доступа", show_alert=True)
        return
    
    await callback.message.edit_text("📢 Функция рассылки будет реализована позже.")
    await callback.answer()