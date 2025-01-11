from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from loader import dp, bot
from states.user import UserStates


@dp.callback_query_handler(F.data.startswith("user_message:"))
async def user_message_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(
        user_id=call.data.split(':')[1]
    )
    await call.message.edit_text(
        text="Javobingizni yuborishdan oldin yaxshilab tekshirib oling, yuborish tugmasi bosilgach xabar foydalanuvchiga "
             "yuboriladi! Jarayonni bekor qilish uchun /bekor qilish buyrug'ini kiriting\n\nJavobingizni kiriting:")
    await UserStates.SEND_MESSAGE_TO_USER.set()


@dp.message_handler(state=UserStates.SEND_MESSAGE_TO_USER)
async def send_message_to_user_handler(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.send_message(
            chat_id=data['user_id'],
            text=f"Savolingizga bot admining javobi:\n\n{message.text}"
        )
        await message.answer("Javobingiz yuborildi!")
        await state.finish()
    except Exception as e:
        await message.answer(f"Xatolik: {str(e)}")
