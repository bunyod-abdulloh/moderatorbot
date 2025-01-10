from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from loader import dp


@dp.message_handler(F.text == "⚙️ Sozlamalar")
async def settings_main_handle(message: types.Message, state: FSMContext):
    await state.finish()
