from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from magic_filter import F

from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import admin_main_buttons
from loader import dp


@dp.message_handler(IsBotAdminFilter(), Command(commands="admin"))
async def admin_main_page(message: types.Message):
    await message.answer("Admin panel", reply_markup=admin_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "🔙 Ortga", state="*")
async def back_to_main_page(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Admin bosh sahifasi!", reply_markup=admin_main_buttons)
