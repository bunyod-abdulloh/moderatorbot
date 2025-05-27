from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from magic_filter import F

from keyboards.default.user import user_main_dkb
from loader import dp, udb
from services.error_service import notify_exception_to_admin


@dp.message_handler(F.text == "/bekor", state="*")
async def bekor_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Jarayon bekor qilindi!")


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = (f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
            f"Guruhlaringizni toza va tartibli saqlashni istaysizmi? Unda Siz to‘g‘ri joydasiz! Bu bot — "
            f"spam va tartibsizliklarga qarshi samarali yechim! 💪\n\n"
            f"📌 <b>Asosiy buyruqlar:</b>"
            f"\n/start - Botni ishga tushirish"
            f"\n/ro - Foydalanuvchini Read Only (yozish huquqini cheklash) rejimiga o'tkazish"
            f"\n/unro - Read Only rejimidan chiqarish\n\n")

    text += ("🤖 <b>Bot quyidagi muhim funksiyalarni bajaradi:</b>\n\n"
             "✅ Guruhga kirgan va chiqqanlik haqidagi xabarlarni avtomatik o‘chiradi\n"
             "✅ Boshqa guruhlardan yuborilgan xabarlarni yo‘q qiladi\n"
             "✅ Har xil reklama, spam va telefon raqamlarini aniqlab, guruhni tozalaydi\n"
             "✅ Guruhga begona botlar qo‘shilishini avtomatik bloklaydi\n"
             "✅ Adminlarga foydalanuvchilarni yozishdan cheklash yoki cheklovdan chiqarish imkonini beradi\n"
             "✅ O‘zi hech qanday reklama tarqatmaydi\n\n"
             "⚠️ <b>Eslatma:</b> Bot to‘liq ishlashi uchun guruhingizda admin huquqiga ega bo‘lishi shart!\n\n"
             )

    try:
        # if message.get_args():
        #     await refdb.add_user_referral(message.get_args(), message.from_user.id)
        #     await message.delete()

        await message.answer(text=text, reply_markup=user_main_dkb)
        await udb.add_user(telegram_id=message.from_user.id)
    except Exception as err:
        await notify_exception_to_admin(err=err)


@dp.message_handler(F.text == "Bosh sahifa")
async def user_main_page(message: types.Message, state: FSMContext):
    await bot_start(message, state)
