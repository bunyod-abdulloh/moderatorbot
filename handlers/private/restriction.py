from aiogram import types
from aiogram.types import ChatPermissions
from aiogram.utils.exceptions import BadRequest
from magic_filter import F

from filters import IsGroupAndBotAdmin
from keyboards.inline.user_ibuttons import (
    restrict_messages_ibuttons, text_callback_data, on_off_restrict_ibuttons
)
from loader import dp, bot, db


# Guruh uchun cheklovlar menyusi
@dp.message_handler(F.text == "✍️ Guruhda xabarlarni cheklash")
async def restrict_messages_main(message: types.Message):
    user_groups = await db.get_group_by_user(telegram_id=message.from_user.id)

    if user_groups:
        await message.answer(
            text="Ushbu bo'limda guruhingizda foydalanuvchilar uchun turli xil cheklovlarni qo'yishingiz yoki o'chirishingiz mumkin"
        )
        for group in user_groups:
            group_name = (await bot.get_chat(group['group_id'])).full_name
            await message.answer(
                text=f"Guruh: {group_name}\n\nKerakli tugmani bosing",
                reply_markup=restrict_messages_ibuttons(group_id=group['group_id'])
            )


# Callback handler: cheklash turini tanlash
@dp.callback_query_handler(text_callback_data.filter())
async def handle_callback_restrict(call: types.CallbackQuery, callback_data: dict):
    callback_type = callback_data["type"]
    group_id = callback_data["group_id"]

    group_name = (await bot.get_chat(group_id)).full_name
    await call.message.edit_text(
        text=f"Guruh: {group_name}\n\nCheklanayotgan xabar turi: {callback_type.capitalize()}",
        reply_markup=on_off_restrict_ibuttons(callback_type, group_id)
    )


@dp.callback_query_handler(F.data.startswith(("offrestrict", "onrestrict")))
async def handle_restrict_action(call: types.CallbackQuery):
    on_off, restrict_type, group_id = call.data.split(":")
    group_id = int(group_id)
    is_enable = on_off == "onrestrict"

    try:
        # Guruhning joriy ruxsatlarini olish
        chat = await bot.get_chat(chat_id=group_id)
        current_permissions = chat.permissions or ChatPermissions()

        # Ruxsatlarni o'zgartirish
        setattr(current_permissions, restrict_type, is_enable)

        # Yangilangan ruxsatlarni qo'llash
        await bot.set_chat_permissions(
            chat_id=group_id,
            permissions=current_permissions,
            use_independent_chat_permissions=True
        )

        await call.message.edit_text(text="Amaliyot muvaffaqqiyatli bajarildi!")
    except BadRequest as e:
        await call.message.edit_text(text=f"Xatolik yuz berdi: {e}")
    except Exception as e:
        await call.message.edit_text(text=f"Kutilmagan xatolik: {e}")


@dp.message_handler(IsGroupAndBotAdmin(), F.text == "salomlar")
async def hello_handler(message: types.Message):
    print(ChatPermissions())
# Callback handler: cheklovlarni yoqish/o'chirish
# @dp.callback_query_handler(F.data.startswith(("offrestrict", "onrestrict")))
# async def handle_restrict_action(call: types.CallbackQuery):
#     on_off, restrict_type, group_id = call.data.split(":")
#     group_id = int(group_id)
#     is_enable = on_off == "onrestrict"
#
#     try:
#         # Guruhning hozirgi ruxsatlarini olish
#         chat = await bot.get_chat(group_id)
#         current_permissions = chat.permissions or ChatPermissions()
#
#         # Ruxsatlarni yangilash
#         setattr(current_permissions, restrict_type, is_enable)
#         await bot.set_chat_permissions(chat_id=group_id, permissions=current_permissions)
#
#         chat = await bot.get_chat(group_id)
#         current_permissions = chat.permissions or ChatPermissions()
#         print(current_permissions)
#         # Yangi ruxsatlarni o'rnatish
#         # await bot.set_chat_permissions(chat_id=group_id, permissions=ChatPermissions(
#         #     can_send_messages=True,
#         #     can_send_media_messages=True,
#         #     can_send_audios=True,
#         #     can_send_documents=True,
#         #     can_send_photos=True,
#         #     can_send_videos=True,
#         #     can_send_video_notes=True,
#         #     can_send_voice_notes=True,
#         #     can_send_polls=True,
#         #     can_send_other_messages=True,
#         #     can_add_web_page_previews=True,
#         #     can_invite_users=True
#         # ))
#
#         await call.message.edit_text(text="Amaliyot muvaffaqqiyatli bajarildi!")
#     except BadRequest:
#         await call.message.edit_text(text="Bot guruhga admin qilinmagan yoki xatolik yuz berdi!")
