import asyncpg.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.exceptions import MessageCantBeDeleted
from keyboards.inline.user_ibuttons import user_main_ibuttons
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

    try:
        if message.get_args():
            await message.delete()
        else:
            await message.answer(text=text_, reply_markup=user_main_ibuttons())
        await db.add_user(message.from_user.id)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    except MessageCantBeDeleted:
        pass
    except Exception:
        pass
    await state.finish()
