import asyncpg.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer(f"Salom, {message.from_user.full_name}!")
    try:
        await db.add_user(message.from_user.id)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    else:
        pass
    await state.finish()
