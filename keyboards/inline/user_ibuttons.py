from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db, bot


def user_main_ibuttons():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text="🤖 Botni guruhga qo'shish", url="https://telegram.me/muhibsamplebot?startgroup=true"),
        InlineKeyboardButton(
            text="➕ Guruhda odam ko'paytirish", callback_data="increase_members"
        ),
        InlineKeyboardButton(
            text="📱 Admin bilan aloqa", callback_data="call_with_admin"
        ))
    return markup


add_user_to_group_ibuttons = InlineKeyboardMarkup(row_width=1)
add_user_to_group_ibuttons.add(InlineKeyboardButton(text="✅ Yoqish", callback_data="on_add_user"))
add_user_to_group_ibuttons.insert(InlineKeyboardButton(text="❌ O'chirish", callback_data="off_add_user"))


async def get_groups_ibuttons(user_groups):
    markup = InlineKeyboardMarkup(row_width=1)
    for group in user_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"usergroup_{group['group_id']}"))
    return markup
