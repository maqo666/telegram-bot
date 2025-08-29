from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from keyboards.inline_kb import get_cancel_keyboard

router = Router()

class EchoState(StatesGroup):
    waiting_for_text = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    async for session in get_db():
        # Проверяем, есть ли пользователь в БД
        stmt = select(User).where(User.user_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            # Создаем нового пользователя
            new_user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name or "Unknown"
            )
            session.add(new_user)
            await session.commit()
            await message.answer("🎉 Добро пожаловать! Вы были зарегистрированы в системе.")
        else:
            await message.answer("👋 С возвращением! Рады видеть вас снова.")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Обработчик команды /profile"""
    async for session in get_db():
        stmt = select(User).where(User.user_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            profile_text = (
                f"📋 Ваш профиль:\n"
                f"👤 ID: {user.user_id}\n"
                f"📛 Имя: {user.first_name}\n"
                f"🌐 Username: @{user.username if user.username else 'нет'}\n"
                f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"📝 Последнее echo: {user.last_echo_text[:50] + '...' if user.last_echo_text and len(user.last_echo_text) > 50 else user.last_echo_text or 'еще не было'}"
            )
            await message.answer(profile_text)
        else:
            await message.answer("❌ Пользователь не найден. Используйте /start для регистрации.")

@router.message(Command("echo"))
async def cmd_echo(message: Message, state: FSMContext):
    """Обработчик команды /echo - запускает FSM"""
    await message.answer(
        "📝 Отправьте мне текст, и я его повторю и сохраню в базу данных:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(EchoState.waiting_for_text)

@router.message(EchoState.waiting_for_text, F.text)
async def process_echo_text(message: Message, state: FSMContext):
    """Обработка текста для эхо"""
    user_text = message.text
    
    async for session in get_db():
        # Сохраняем текст в базу данных
        stmt = select(User).where(User.user_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.last_echo_text = user_text
            await session.commit()
        
        # Отправляем эхо-сообщение
        await message.answer(f"🔁 Эхо: {user_text}")
        await state.clear()

@router.message(EchoState.waiting_for_text)
async def process_echo_invalid(message: Message):
    """Обработка некорректного ввода в состоянии echo"""
    await message.answer("❌ Пожалуйста, отправьте текстовое сообщение.")

@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены действия"""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.answer()