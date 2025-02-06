from typing import List
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotKicked, MigrateToChat
from magic_filter import F

from data.config import BOT_ID
from loader import dp, bot, db
from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import group_main_buttons
from keyboards.inline.admin_ibuttons import view_groups_ibutton, group_button
from states.admin import AdminStates
from utils.user_functions import extracter, logging_text

# Xabarlar va ogohlantirish matni
WARNING_TEXT = (
    "Habar yuborishdan oldin postingizni yaxshilab tekshirib oling!\n\n"
    "Imkoni bo'lsa postingizni oldin tayyorlab olib keyin yuboring.\n\n"
    "Habaringizni kiriting:"
)


# Yordamchi funksiyalar
async def handle_media_group(album: List[types.Message]) -> types.MediaGroup:
    """MediaGroup obyektini yaratish."""
    media_group = types.MediaGroup()
    for obj in album:
        file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
        media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption})
    return media_group


async def paginate_groups(call: types.CallbackQuery, current_page: int, next_page=False, prev_page=False):
    """Guruhlar ro'yxatini sahifalash."""
    all_groups = await db.get_groups()
    extract = extracter(all_datas=all_groups, delimiter=10)
    total_pages = len(extract)

    current_page = (
        current_page + 1 if next_page and current_page < total_pages else
        current_page - 1 if prev_page and current_page > 1 else
        current_page
    )

    groups_on_page = extract[current_page - 1]
    markup = await view_groups_ibutton(groups_on_page, current_page, total_pages)
    try:
        await call.answer(cache_time=0)
        await call.message.edit_text("Kerakli guruh tugmasiga bosing", reply_markup=markup)
    except Exception:
        pass


async def handle_group_info_(group_id, call: types.CallbackQuery):
    chat = await bot.get_chat(chat_id=group_id)
    check_blacklist = await db.get_group_by_blacklist(group_id)
    get_group_on_db = await db.get_group(group_id)

    user = await bot.get_chat_member(group_id, get_group_on_db['user_id'])
    bot_status = (await bot.get_chat_member(group_id, BOT_ID)).status

    await call.message.edit_text(
        (
            f"Guruh ma'lumotlari\n\n"
            f"Guruh nomi: {chat.full_name}\n"
            f"Guruh username: @{chat.username}\n"
            f"Foydalanuvchilar soni: {await bot.get_chat_member_count(group_id)}\n"
            f"Mas'ul: {user.user.full_name}\n"
            f"Username: @{user.user.username}\n"
            f"Status: {user.status.capitalize()}\n"
            f"Bot guruhga qo'shilgan sana: {get_group_on_db['created_at']}\n"
            f"Botni ushbu guruhda foydalanish holati: {check_blacklist}\n"
            f"Botni guruhdagi statusi: {bot_status.capitalize()}"
        ),
        reply_markup=group_button(group_id)
    )


# Handlerlar
@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar")
async def groups_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(message.text, reply_markup=group_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message, state: FSMContext):
    await state.finish()
    all_groups = await db.get_groups()
    if not all_groups:
        await message.answer("Guruhlar mavjud emas!")
        return

    extract = extracter(all_datas=all_groups, delimiter=10)
    markup = await view_groups_ibutton(extract[0], current_page=1, all_pages=len(extract))
    await message.answer("Kerakli guruh tugmasiga bosing", reply_markup=markup)


@dp.callback_query_handler(F.data.startswith(("alert_", "next_", "prev_")))
async def navigation_callback(call: types.CallbackQuery):
    action, current_page = call.data.split("_")
    current_page = int(current_page)

    if action == "alert":
        await call.answer(f"Siz {current_page} - sahifadasiz!", show_alert=True)
    else:
        await paginate_groups(call, current_page, next_page=(action == "next"), prev_page=(action == "prev"))


@dp.callback_query_handler(F.data.startswith("getgroup_"))
async def handle_group_info(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    try:
        await handle_group_info_(group_id, call)
    except MigrateToChat as err:
        new_id = err.migrate_to_chat_id
        await db.update_group_id(new_id, group_id)
        # Xatolikdan keyin funksiyani qayta chaqirish
        await handle_group_info_(new_id, call)
    except Exception as err:
        await logging_text(err)


@dp.callback_query_handler(F.data.startswith(("post_to_group:", "media_to_group:")))
async def send_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    action, group_id = call.data.split(":")
    await state.update_data(group_id=int(group_id))
    await call.message.edit_text(WARNING_TEXT)
    await (AdminStates.SEND_POST_TO_GROUP if action == "post_to_group" else AdminStates.SEND_MEDIA_TO_GROUP).set()


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUP, content_types=types.ContentTypes.ANY)
async def send_to_group_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group_id = data.get("group_id")
    try:
        await message.copy_to(chat_id=group_id)
        group_name = (await bot.get_chat(chat_id=group_id)).full_name
        await message.answer(f"Xabar {group_name} ga yuborildi!")
    except BotKicked:
        await db.delete_group(group_id)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
    await state.finish()


@dp.message_handler(state=AdminStates.SEND_MEDIA_TO_GROUP, content_types=types.ContentTypes.ANY, is_media_group=True)
async def send_to_group_media(message: types.Message, album: List[types.Message], state: FSMContext):
    data = await state.get_data()
    group_id = data.get("group_id")
    media_group = await handle_media_group(album)
    try:
        await bot.send_media_group(group_id, media_group)
        group_name = (await bot.get_chat(chat_id=group_id)).full_name
        await message.answer(f"Xabar {group_name} ga yuborildi!")
    except BotKicked:
        await db.delete_group(group_id)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
    await state.finish()


@dp.callback_query_handler(F.data == "back_to_groups")
async def back_to_group_callback(call: types.CallbackQuery):
    all_groups = await db.get_groups()
    extract = extracter(all_datas=all_groups, delimiter=10)
    markup = await view_groups_ibutton(extract[0], current_page=1, all_pages=len(extract))
    await call.message.edit_text("Kerakli guruh tugmasiga bosing", reply_markup=markup)
