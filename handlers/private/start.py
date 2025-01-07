import asyncpg.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from magic_filter import F

from keyboards.default.user_dbuttons import user_main_dbuttons
from loader import dp, db


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    text = (f"Salom, {message.from_user.full_name}!\n\n"
            f"Buyruqlar"
            f"\n\n/start - Botni ishga tushirish"
            f"\n/admin - Admin panel"
            f"\n/ro - Foydalanuvchini Read Only rejimiga o'tkazish"
            f"\n/unro - RO rejimidan chiqarish"
            f"\n/ban - Ban"
            f"\n/unban - Bandan chiqarish"
            f"\n\nUshbu buyruqlar botni biror guruhga admin qilganingizda ishlaydi!")
    text_ = ("Assalom aleykum!\n\nBu bot orqali siz guruhingizdagi ruxsatsiz jo'natilgan reklamalarni o'chiraman "
             "(jpg, telefon) raqam, havola) shakldagilarni, hamda guruhga foydalanuvchi chiqgani va kirgani haqidagi "
             "xabarni o'chiraman. Mendan to'laqonli foydalanish uchun guruhingizga qo'shib keyin adminlik berishingiz "
             "kerak. Meni boshqa botlardan afzalligim reklamalar jo'natmayman.")
    await message.answer(text=text_, reply_markup=user_main_dbuttons)

    try:
        await db.add_user(message.from_user.id)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    else:
        pass
    await state.finish()
