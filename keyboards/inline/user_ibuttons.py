from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import bot

text_callback_data = CallbackData("action", "type", "group_id")

text_callback = {
    "Matn": "can_send_messages",
    "Audio": "can_send_audios",
    "Document": "can_send_documents",
    "Photo": "can_send_photos",
    "Video": "can_send_videos",
    "Video xabar": "can_send_video_notes",
    "Ovozli xabar": "can_send_voice_notes",
    "Poll": "can_send_polls",
    "Boshqa": "can_send_other_messages"
}


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


def restrict_messages_ibuttons(group_id):
    markup = InlineKeyboardMarkup(row_width=3)

    for text, callback in text_callback.items():
        markup.insert(
            InlineKeyboardButton(text=text, callback_data=text_callback_data.new(type=callback, group_id=group_id)))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_user"))
    return markup


def on_off_restrict_ibuttons(type_, group_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="❌ O'chirish", callback_data=f"offrestrict:{type_}:{group_id}"))
    markup.insert(InlineKeyboardButton(text="✅ Yoqish", callback_data=f"onrestrict:{type_}:{group_id}"))
    return markup
