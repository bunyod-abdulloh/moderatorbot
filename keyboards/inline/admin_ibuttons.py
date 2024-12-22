from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db, bot

admin_check = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Ha", callback_data="send_to_bot_yes"
        ), InlineKeyboardButton(
            text="Yo'q", callback_data="send_to_bot_no"
        )
    ]]
)


async def view_groups_ibutton():
    all_groups = await db.get_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    for group in all_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"getgroup_{group['group_id']}"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_admin_main"))
    return markup


def group_button(group_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="Habar yuborish", callback_data=f"send_to_group:{group_id}"))
    return markup
