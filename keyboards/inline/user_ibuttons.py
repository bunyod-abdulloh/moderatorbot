from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import bot

# CallbackData obyekti
text_callback_data = CallbackData("action", "type", "group_id")

# Xabar turlari va matnlarni lug‘ati
text_callback = {
    "can_send_messages": "Matn",
    "can_send_audios": "Audio",
    "can_send_documents": "Document",
    "can_send_photos": "Photo",
    "can_send_videos": "Video",
    "can_send_video_notes": "Video xabar",
    "can_send_voice_notes": "Ovozli xabar",
    "can_send_polls": "Poll",
    "can_send_other_messages": "Stiker/GIF"
}


def user_main_ibuttons():
    """Botni guruhga qo‘shish uchun tugma."""
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text="🤖 Botni guruhga qo'shish",
            url="https://telegram.me/muhibsamplebot?startgroup=true"
        )
    )


add_user_to_group_ibuttons = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="✅ Yoqish", callback_data="on_increase"),
    InlineKeyboardButton(text="❌ O'chirish", callback_data="off_increase")
)


async def get_groups_ibuttons(user_groups, off_add_user=False):
    """Foydalanuvchi guruhlari ro'yxati uchun tugmalar."""
    markup = InlineKeyboardMarkup(row_width=1)
    action = "increase_off" if off_add_user else "increase_on"
    for group in user_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"{action}:{group['group_id']}"))
    return markup


def send_message_to_admin(user_id):
    """Administratorga foydalanuvchi haqida xabar yuborish tugmasi."""
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Javob yuborish", callback_data=f"user_message:{user_id}")
    )


async def restrict_groups_ibutton(all_groups, current_page, all_pages):
    """Cheklov qo‘yish uchun guruhlarni sahifalab ko‘rsatish tugmalari."""
    markup = InlineKeyboardMarkup(row_width=3)

    for group in all_groups:
        group_name = (await bot.get_chat(chat_id=group['group_id'])).full_name
        markup.add(
            InlineKeyboardButton(text=group_name, callback_data=f"userrestrict:{group['group_id']}")
        )

    # Navigatsiya tugmalari
    navigation_buttons = [
        InlineKeyboardButton(text="◀️", callback_data=f"prev-restrict:{current_page}"),
        InlineKeyboardButton(text=f"{current_page}/{all_pages}", callback_data=f"alert-restrict:{current_page}"),
        InlineKeyboardButton(text="▶️", callback_data=f"next-restrict:{current_page}")
    ]
    markup.row(*navigation_buttons)

    return markup


def restrict_messages_ibuttons(group_id):
    """Guruhda xabar turlarini cheklash tugmalari."""
    markup = InlineKeyboardMarkup(row_width=3)
    for callback, text in text_callback.items():
        markup.insert(
            InlineKeyboardButton(
                text=text,
                callback_data=text_callback_data.new(type=callback, group_id=group_id)
            )
        )
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_restrict"))
    return markup


def on_off_restrict_ibuttons(type_, group_id):
    """Xabar turlarini yoqish yoki o‘chirish uchun tugmalar."""
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text="❌ Cheklash", callback_data=f"offrestrict:{type_}:{group_id}"),
        InlineKeyboardButton(text="✅ Yoqish", callback_data=f"onrestrict:{type_}:{group_id}"),
        InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_restrict")
    )
