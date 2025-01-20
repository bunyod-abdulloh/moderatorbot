from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot


async def view_groups_ibutton(all_groups, current_page, all_pages):
    markup = InlineKeyboardMarkup(row_width=3)

    for group in all_groups:
        group_name = (await bot.get_chat(chat_id=group['group_'])).full_name
        markup.add(InlineKeyboardButton(text=group_name, callback_data=f"getgroup_{group['group_']}"))

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
    markup.insert(InlineKeyboardButton(text="Oddiy xabar yuborish", callback_data=f"post_to_group:{group_id}"))
    markup.insert(
        InlineKeyboardButton(text="Mediagroup xabar yuborish", callback_data=f"media_to_group:{group_id}"))
    markup.insert(InlineKeyboardButton(text="Botni guruhda cheklash", callback_data=f"restrictbot:{group_id}"))
    markup.insert(InlineKeyboardButton(text="Botni guruhdan chiqarish", callback_data=f"leftbot:{group_id}"))
    markup.insert(InlineKeyboardButton(text="◀️ Ortga", callback_data=f"back_to_groups"))
    return markup


async def view_referrals_ibutton(all_referrals, current_page, all_pages):
    markup = InlineKeyboardMarkup(row_width=3)

    for referral in all_referrals:
        markup.add(InlineKeyboardButton(text=referral['name'], callback_data=f"getreferral_{referral['id']}"))

    markup.add(
        InlineKeyboardButton(
            text="◀️",
            callback_data=f"ref:prev_{current_page}"
        ))
    markup.insert(InlineKeyboardButton(
        text=f"{current_page}/{all_pages}",
        callback_data=f"ref:alert_{current_page}"
    ))
    markup.insert(InlineKeyboardButton(
        text="▶️",
        callback_data=f"ref:next_{current_page}"))
    return markup


def back_to_ref_main(ref_id=None):
    markup = InlineKeyboardMarkup(row_width=1)
    if ref_id:
        markup.add(InlineKeyboardButton(text="O'chirish", callback_data=f"ref:del_{ref_id}"))
    markup.insert(InlineKeyboardButton(text="◀️ Ortga", callback_data="back_to_ref_main"))
    return markup
