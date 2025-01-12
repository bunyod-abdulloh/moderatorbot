import asyncio

from typing import List
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotKicked
from magic_filter import F
from loader import dp, bot, db
from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import group_main_buttons
from keyboards.inline.admin_ibuttons import view_groups_ibutton, group_button
from states.admin import AdminStates
from utils.user_functions import extracter

# Yordamchi matnlar
WARNING_TEXT = (
    "Habar yuborishdan oldin postingizni yaxshilab tekshirib oling!\n\n"
    "Imkoni bo'lsa postingizni oldin tayyorlab olib keyin yuboring.\n\n"
    "Habaringizni kiriting:"
)


async def get_group_info(group_id):
    """
    Guruh haqida ma'lumotlarni olish.
    """
    chat = await bot.get_chat(chat_id=group_id)
    return {
        "name": chat.full_name,
        "username": chat.username,
        "member_count": await bot.get_chat_member_count(chat_id=group_id)
    }


async def handle_media_group(album: List[types.Message]) -> types.MediaGroup:
    """
    Media-guruhni qayta ishlash.
    """
    media_group = types.MediaGroup()
    for obj in album:
        file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
        media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption})
    return media_group


async def paginate_groups(call: types.CallbackQuery, current_page: int, next_page=False, prev_page=False):
    all_groups = await db.get_groups()

    extract = extracter(all_datas=all_groups, delimiter=10)
    if next_page:
        current_page = current_page + 1 if current_page < len(extract) else 1
    if prev_page:
        current_page = current_page - 1 if current_page > 1 else len(extract)
    groups_on_page = extract[current_page - 1]

    markup = await view_groups_ibutton(
        all_groups=groups_on_page, current_page=current_page, all_pages=len(extract)
    )
    await call.message.edit_text(
        text="Kerakli guruh tugmasiga bosing", reply_markup=markup
    )


async def send_to_groups(message: types.Message, groups: List[dict], media_group=None):
    """
    Guruhlarga xabar yoki media-guruh yuborish.
    """
    success_count, failed_count = 0, 0
    for group in groups:
        try:
            if media_group:
                await bot.send_media_group(chat_id=group['group_id'], media=media_group)
            else:
                await message.copy_to(chat_id=group['group_id'])
            success_count += 1
        except BotKicked:
            failed_count += 1
            await db.delete_group(group['group_id'])
        if success_count % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    return success_count, failed_count


# Handlerlar
@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar")
async def groups_handler(message: types.Message):
    await message.answer(text=message.text, reply_markup=group_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message):
    all_groups = await db.get_groups()
    if not all_groups:
        await message.answer("Guruhlar mavjud emas!")
    else:
        extract = extracter(all_datas=all_groups, delimiter=10)
        await message.answer(
            text="Kerakli guruh tugmasiga bosing",
            reply_markup=await view_groups_ibutton(
                all_groups=extract[0], current_page=1, all_pages=len(extract)
            )
        )


@dp.callback_query_handler(F.data.startswith(("alert_", "next_", "prev_")))
async def navigation_callback(call: types.CallbackQuery):
    action, current_page = call.data.split("_")
    current_page = int(current_page)

    if action == "alert":
        await call.answer(text=f"Siz {current_page} - sahifadasiz!", show_alert=True)
    elif action == "next":
        await call.answer(cache_time=0)
        await paginate_groups(call=call, current_page=current_page, next_page=True)
    elif action == "prev":
        await call.answer(cache_time=0)
        await paginate_groups(call=call, current_page=current_page, prev_page=True)


@dp.callback_query_handler(F.data.startswith("getgroup_"))
async def get_groups_handler(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    group_info = await get_group_info(group_id)
    get_group_on_db = await db.get_group(group_id)
    user = await bot.get_chat_member(group_id, get_group_on_db['telegram_id'])

    await call.message.edit_text(
        text=(
            f"Guruh ma'lumotlari:\n\n"
            f"Guruh nomi: {group_info['name']}\n"
            f"Guruh username: @{group_info['username']}\n"
            f"Foydalanuvchilar soni: {group_info['member_count']}\n"
            f"Mas'ul: {user.user.full_name}\n"
            f"Username: @{user.user.username}\n"
            f"Status: {user.status.capitalize()}"
        ),
        reply_markup=group_button(group_id=group_id)
    )


@dp.callback_query_handler(F.data.startswith("send_post_to_group:"))
async def send_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    group_id = call.data.split(":")[1]
    await state.update_data(group_id=group_id)
    await call.message.edit_text(text=WARNING_TEXT)
    await AdminStates.SEND_POST_TO_GROUP.set()


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUP, content_types=types.ContentTypes.ANY)
async def send_to_group_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group_id = int(data.get("group_id"))
    try:
        await message.copy_to(chat_id=group_id)
        group_name = (await bot.get_chat(chat_id=group_id)).full_name
        await message.answer(f"{group_name} ga habar yuborildi!")
    except BotKicked:
        await db.delete_group(group_id)
    await state.finish()


@dp.callback_query_handler(F.data == "back_to_groups")
async def back_to_group_callback(call: types.CallbackQuery):
    await call.answer(cache_time=0)
    all_groups = await db.get_groups()

    extract = extracter(all_datas=all_groups, delimiter=10)
    await call.message.edit_text(
        text="Kerakli guruh tugmasiga bosing", reply_markup=await view_groups_ibutton(
            all_groups=extract[0], current_page=1, all_pages=len(extract)
        )
    )
