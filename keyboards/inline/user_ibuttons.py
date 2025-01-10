from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot


def user_main_ibuttons():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text="🤖 Botni guruhga qo'shish", url="https://telegram.me/muhibsamplebot?startgroup=true"))
    return markup


add_user_to_group_ibuttons = InlineKeyboardMarkup(row_width=1)
add_user_to_group_ibuttons.add(InlineKeyboardButton(text="✅ Yoqish", callback_data="on_increase"))
add_user_to_group_ibuttons.insert(InlineKeyboardButton(text="❌ O'chirish", callback_data="off_increase"))


async def get_groups_ibuttons(user_groups, off_add_user=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for group in user_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        if off_add_user:
            markup.add(InlineKeyboardButton(text=group_name, callback_data=f"increase_off:{group['group_id']}"))
        else:
            markup.add(InlineKeyboardButton(text=group_name, callback_data=f"increase_on:{group['group_id']}"))
    return markup


def send_message_to_admin(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="Javob yuborish", callback_data=f"user_message:{user_id}"))
    return markup
