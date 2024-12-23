import asyncpg.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer(f"Salom, {message.from_user.full_name}!\n\n"
                         f"Buyruqlar"
                         f"\n\n/start - Botni ishga tushirish"
                         f"\n/admin - Admin panel"
                         f"\n/ro - Foydalanuvchini Read Only rejimiga o'tkazish"
                         f"\n/unro - RO rejimidan chiqarish"
                         f"\n/ban - Ban"
                         f"\n/unban - Bandan chiqarish"
                         f"\n\nUshbu buyruqlar botni biror guruhga admin qilganingizda ishlaydi!")

    try:
        await db.add_user(message.from_user.id)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    else:
        pass
    await state.finish()
