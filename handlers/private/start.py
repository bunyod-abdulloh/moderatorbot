from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from magic_filter import F

from keyboards.default.user_dbuttons import user_main_dbuttons
from keyboards.inline.user_ibuttons import user_main_ibuttons
from loader import dp, db, bot
from utils.user_functions import logging_text


@dp.message_handler(F.text == "/bekor", state="*")
async def bekor_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Jarayon bekor qilindi!", reply_markup=user_main_dbuttons)


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    # text = (f"Salom, {message.from_user.full_name}!\n\n"
    #         f"Buyruqlar"
    #         f"\n\n/start - Botni ishga tushirish"
    #         f"\n/admin - Admin panel"
    #         f"\n/ro - Foydalanuvchini Read Only rejimiga o'tkazish"
    #         f"\n/unro - RO rejimidan chiqarish"
    #         f"\n/ban - Ban"
    #         f"\n/unban - Bandan chiqarish"
    #         f"\n\nUshbu buyruqlar botni biror guruhga admin qilganingizda ishlaydi!")
    # text_ = ("Bu bot orqali siz guruhingizdagi ruxsatsiz jo'natilgan reklamalarni o'chiraman "
    #          "(jpg, telefon) raqam, havola) shakldagilarni, hamda guruhga foydalanuvchi chiqgani va kirgani haqidagi "
    #          "xabarni o'chiraman. Mendan to'laqonli foydalanish uchun guruhingizga qo'shib keyin adminlik berishingiz "
    #          "kerak. Meni boshqa botlardan afzalligim reklamalar jo'natmayman.")
    #
    # try:
    #     if message.get_args():
    #         await db.add_user_referral(message.get_args(), message.from_user.id)
    #         await message.delete()
    #     await bot.send_message(chat_id=message.from_user.id,
    #                            text="Assalomu alaykum!", reply_markup=user_main_dbuttons)
    #
    #     await message.answer(text=text_, reply_markup=user_main_ibuttons())
    #     await db.add_user(message.from_user.id)
    # except Exception as err:
    #     await logging_text(err)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton(text="A", callback_data="kimyo"),
               types.InlineKeyboardButton(text="B", callback_data="biologiya"))
    markup.row(types.InlineKeyboardButton(text="C", callback_data="biologiya"),
               types.InlineKeyboardButton(text="D", callback_data="kimyo"))


    await message.answer_photo(
        photo="AgACAgIAAxkBAAIJbmemIMy2OXDNXO64jW13DhbiA6NGAAKx7TEbURY4SSvXbfCFgZPOAQADAgADeQADNgQ", reply_markup=markup
    )

# @dp.message_handler(content_types=types.ContentTypes.PHOTO, state="*")
# async def get_photo(message: types.Message):
#     await message.answer(
#         text=f"<code>{message.photo[-1].file_id}</code>"
#     )




# @dp.callback_query_handler(F.data == "kimyo")
# async def kimyo_test(call: types.CallbackQuery):
#     button = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     button.row("📚📚 Kimyo DTM Testlar ✅")
#     button.row("📚📚 Kimyo Milliy Sertifikat Testlar ✅")
#     button.row("Ortga")
#     await call.message.delete()
#     await call.message.answer(text="Kimyodan testlar to'plami", reply_markup=button)


@dp.message_handler(F.text == "Bosh sahifa")
async def user_main_page(message: types.Message, state: FSMContext):
    await bot_start(message, state)
