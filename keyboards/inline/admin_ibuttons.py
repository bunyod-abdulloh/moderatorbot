from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot


async def view_groups_ibutton(all_groups, current_page, all_pages):
    markup = InlineKeyboardMarkup(row_width=3)
    for group in all_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"getgroup_{group['group_id']}"))
    markup.add(
        InlineKeyboardButton(
            text="◀️",
            callback_data=f"prev_{current_page}"
        ))
    markup.insert(InlineKeyboardButton(
        text=f"{current_page}/{all_pages}",
        callback_data=f"alert_{current_page}"
    ))
    markup.insert(InlineKeyboardButton(
        text="▶️",
        callback_data=f"next_{current_page}"))
    return markup


def group_button(group_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="Oddiy xabar yuborish", callback_data=f"send_post_to_group:{group_id}"))
    markup.add(
        InlineKeyboardButton(text="Mediagroup xabar yuborish", callback_data=f"send_media_to_group:{group_id}"))
    return markup


def button_generator(current_page: int, all_pages: int):
    key = InlineKeyboardMarkup(
        row_width=3
    )
    key.add(
        InlineKeyboardButton(
            text="◀️",
            callback_data=f"prev_{current_page}"
        ))
    key.insert(InlineKeyboardButton(
        text=f"{current_page}/{all_pages}",
        callback_data=f"alert_{current_page}"
    ))
    key.insert(InlineKeyboardButton(
        text="▶️",
        callback_data=f"next_{current_page}"
    )

    )
    return key
