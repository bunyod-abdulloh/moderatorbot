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

WARNING_TEXT = (
    "Habar yuborishdan oldin postingizni yaxshilab tekshirib oling!\n\n"
    "Imkoni bo'lsa postingizni oldin tayyorlab olib keyin yuboring.\n\n"
    "Habaringizni kiriting:"
)


async def get_group_info(group_id):
    chat = await bot.get_chat(chat_id=group_id)
    return {
        "name": chat.full_name,
        "username": chat.username,
        "member_count": await bot.get_chat_member_count(chat_id=group_id)
    }


async def handle_media_group(album: List[types.Message]) -> types.MediaGroup:
    media_group = types.MediaGroup()
    for obj in album:
        file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
        media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption})
    return media_group


async def paginate_groups(call: types.CallbackQuery, current_page: int, next_page=False, prev_page=False):
    try:
        all_groups = await db.get_groups()
        extract = extracter(all_datas=all_groups, delimiter=10)
        total_pages = len(extract)

        if next_page:
            current_page = current_page + 1 if current_page < total_pages else 1
        elif prev_page:
            current_page = current_page - 1 if current_page > 1 else total_pages

        groups_on_page = extract[current_page - 1]

        markup = await view_groups_ibutton(
            all_groups=groups_on_page, current_page=current_page, all_pages=total_pages
        )
        await call.message.edit_text("Kerakli guruh tugmasiga bosing", reply_markup=markup)
    except Exception:
        pass


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar")
async def groups_handler(message: types.Message):
    await message.answer(message.text, reply_markup=group_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message):
    all_groups = await db.get_groups()
    if not all_groups:
        await message.answer("Guruhlar mavjud emas!")
    else:
        extract = extracter(all_datas=all_groups, delimiter=10)
        await message.answer(
            "Kerakli guruh tugmasiga bosing",
            reply_markup=await view_groups_ibutton(all_groups=extract[0], current_page=1, all_pages=len(extract))
        )


@dp.callback_query_handler(F.data.startswith(("alert_", "next_", "prev_")))
async def navigation_callback(call: types.CallbackQuery):
    action, current_page = call.data.split("_")
    current_page = int(current_page)

    if action == "alert":
        await call.answer(f"Siz {current_page} - sahifadasiz!", show_alert=True)
    else:
        await call.answer(cache_time=0)
        await paginate_groups(call, current_page, next_page=(action == "next"), prev_page=(action == "prev"))


@dp.callback_query_handler(F.data.startswith("getgroup_"))
async def get_groups_handler(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    group_info = await get_group_info(group_id)
    get_group_on_db = await db.get_group(group_id)
    user = await bot.get_chat_member(group_id, get_group_on_db['telegram_id'])

    await call.message.edit_text(
        (
            f"Guruh ma'lumotlari\n\n"
            f"Guruh nomi: {group_info['name']}\n"
            f"Guruh username: @{group_info['username']}\n"
            f"Foydalanuvchilar soni: {group_info['member_count']}\n"
            f"Mas'ul: {user.user.full_name}\n"
            f"Username: @{user.user.username}\n"
            f"Status: {user.status.capitalize()}"
        ),
        reply_markup=group_button(group_id=group_id)
    )


@dp.callback_query_handler(F.data.startswith(("post_to_group:", "media_to_group:")))
async def send_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    action, group_id = call.data.split(":")
    await state.update_data(group_id=group_id)
    await call.message.edit_text(WARNING_TEXT)

    await (AdminStates.SEND_POST_TO_GROUP if action == "post_to_group" else AdminStates.SEND_MEDIA_TO_GROUP).set()


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUP, content_types=types.ContentTypes.ANY)
async def send_to_group_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group_id = int(data.get("group_id"))
    try:
        await message.copy_to(chat_id=group_id)
        group_name = (await bot.get_chat(chat_id=group_id)).full_name
        await message.answer(f"Xabar {group_name} ga yuborildi!")
    except BotKicked:
        await db.delete_group(group_id)
    except Exception:
        pass
    await state.finish()


@dp.message_handler(state=AdminStates.SEND_MEDIA_TO_GROUP, content_types=types.ContentTypes.ANY, is_media_group=True)
async def send_to_group_media(message: types.Message, album: List[types.Message], state: FSMContext):
    media_group = await handle_media_group(album)
    data = await state.get_data()
    try:
        await bot.send_media_group(data['group_id'], media_group)
        group_name = (await bot.get_chat(chat_id=data['group_id'])).full_name
        await message.answer(f"Xabar {group_name} ga yuborildi!")
    except BotKicked:
        await db.delete_group(data['group_id'])
    except Exception:
        pass
    await state.finish()


@dp.callback_query_handler(F.data == "back_to_groups")
async def back_to_group_callback(call: types.CallbackQuery):
    await call.answer(cache_time=0)
    all_groups = await db.get_groups()
    extract = extracter(all_datas=all_groups, delimiter=10)
    await call.message.edit_text(
        "Kerakli guruh tugmasiga bosing",
        reply_markup=await view_groups_ibutton(all_groups=extract[0], current_page=1, all_pages=len(extract))
    )
