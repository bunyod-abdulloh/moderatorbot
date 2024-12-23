from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db, bot


async def view_groups_ibutton():
    all_groups = await db.get_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    for group in all_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"getgroup_{group['group_id']}"))
    return markup


def group_button(group_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="Oddiy xabar yuborish", callback_data=f"send_post_to_group:{group_id}"))
    markup.add(
        InlineKeyboardButton(text="Mediagroup xabar yuborish", callback_data=f"send_media_to_group:{group_id}"))
    return markup
