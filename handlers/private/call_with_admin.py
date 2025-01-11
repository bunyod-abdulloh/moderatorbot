from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from data.config import ADMINS
from keyboards.inline.user_ibuttons import send_message_to_admin
from loader import dp, bot
from states.user import UserStates
from utils.user_functions import cancel_text


@dp.message_handler(F.text == "📱 Admin bilan aloqa")
async def call_with_admin_callback(message: types.Message):
    await message.answer(
        f"Xabaringizni yuborishdan oldin yaxshilab tekshirib oling, yuborish tugmasini bosishingiz bilan "
        f"xabar adminga yuboriladi.\n{cancel_text}\n\nXabaringizni kiriting:")
    await UserStates.CALL_WITH_ADMIN.set()


@dp.message_handler(state=UserStates.CALL_WITH_ADMIN)
async def call_with_admin_two(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(
        chat_id=ADMINS[0], text=f"Savol qabul qilindi!\n\n"
                                f"Username: @{message.from_user.username}\n\n"
                                f"Savol:\n\n{message.text}", reply_markup=send_message_to_admin(
            message.from_user.id
        )
    )
    await message.answer("Xabaringiz qabul qilindi va adminga yuborildi!")
