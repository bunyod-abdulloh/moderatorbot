from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import group_main_buttons
from keyboards.inline.admin_ibuttons import view_groups_ibutton, group_button
from loader import dp, bot, db

warning_text = (
    "Habar yuborishdan oldin postingizni yaxshilab tekshirib oling!\n\nImkoni bo'lsa postingizni oldin tayyorlab "
    "olib keyin yuboring.\n\nHabaringizni kiriting:")


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar")
async def groups_handler(message: types.Message):
    await message.answer(text=message.text, reply_markup=group_main_buttons
                         )


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message):
    await message.answer(
        text="Kerakli guruh tugmasiga bosing", reply_markup=await view_groups_ibutton()
    )


@dp.callback_query_handler(F.data.startswith("getgroup_"))
async def get_groups_handler(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    group_name = (await bot.get_chat(chat_id=group_id)).full_name
    group_username = (await bot.get_chat(chat_id=group_id)).username
    count_members = await bot.get_chat_member_count(chat_id=group_id)
    await call.message.edit_text(
        text=f"Guruh ma'lumotlari:\n\n"
             f"Guruh nomi: {group_name}\n"
             f"Guruh username: @{group_username}\n"
             f"Foydalanuvchilar soni: {count_members}",
        reply_markup=group_button(group_id=group_id)
    )


@dp.callback_query_handler(F.data.startswith("send_to_group:"))
async def send_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    group_id = call.data.split(":")[1]
    await state.update_data(group_id=group_id)
    await call.message.edit_text(text=warning_text)
    await state.set_state("send_to_group")


@dp.message_handler(state="send_to_group", content_types=['any'])
async def send_to_group_two(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group_id = int(data.get("group_id"))
    await message.copy_to(chat_id=group_id)
    group_name = (await bot.get_chat(chat_id=group_id)).full_name
    await message.answer(f"{group_name} ga habar yuborildi!")
    await state.finish()


@dp.message_handler(F.text == "salla")
async def salla_handler(message: types.Message):
    for n in range(4000):
        await db.add_user(telegram_id=message.from_user.id)
    await message.answer("Qo'shildi!")
