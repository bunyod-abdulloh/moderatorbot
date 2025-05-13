from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.user_dbuttons import user_main_dbuttons
from magic_filter import F

from keyboards.inline.user_ibuttons import user_main_ibuttons
from loader import dp, db
from services.error_service import notify_exception_to_admin


@dp.message_handler(F.text == "/bekor", state="*")
async def bekor_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Jarayon bekor qilindi!", reply_markup=user_main_dbuttons)


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = (f"Salom, {message.from_user.full_name}!\n\n"
            f"Buyruqlar"
            f"\n\n/start - Botni ishga tushirish"
            f"\n/admin - Admin panel"
            f"\n/ro - Foydalanuvchini Read Only rejimiga o'tkazish"
            f"\n/unro - RO rejimidan chiqarish"
            f"\n/ban - Ban"
            f"\n/unban - Bandan chiqarish"
            f"\n\nUshbu buyruqlar botni biror guruhga admin qilganingizda ishlaydi!")
    text += ("Bu bot orqali siz guruhingizdagi ruxsatsiz jo'natilgan reklamalarni o'chiraman "
             "(jpg, telefon) raqam, havola) shakldagilarni, hamda guruhga foydalanuvchi chiqgani va kirgani haqidagi "
             "xabarni o'chiraman. Mendan to'laqonli foydalanish uchun guruhingizga qo'shib keyin adminlik berishingiz "
             "kerak. Meni boshqa botlardan afzalligim reklamalar jo'natmayman.")

    try:
        if message.get_args():
            await db.add_user_referral(message.get_args(), message.from_user.id)
            await message.delete()

        await message.answer(text=text, reply_markup=user_main_ibuttons())
        await db.add_user(telegram_id=message.from_user.id)
    except Exception as err:
        await notify_exception_to_admin(err=err)


@dp.message_handler(F.text == "Bosh sahifa")
async def user_main_page(message: types.Message, state: FSMContext):
    await bot_start(message, state)
