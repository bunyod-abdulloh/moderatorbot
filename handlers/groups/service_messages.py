import aiogram
from aiogram import types
from magic_filter import F

from data.config import ADMINS, BOT_ID
from filters.group_chat import IsGroup, IsGroupPhoto, is_admin
from loader import dp, bot, db


async def alert_message(alert_text, message: types.Message):
    text = (f"Bot guruhga admin qilinmaganligi sababli foydalanuvchi {alert_text} haqidagi habarni "
            "o'chirmadi!\n\nBot to'g'ri ishlashi uchun botni guruhga admin qilishingiz lozim!")
    await message.answer(text)


# async def send_alert(message, text):
#     """Common function to send alert message and delete the original."""
#     await message.answer(text)


@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    try:
        member_mentions = []

        # Iterate through new members
        for member in message.new_chat_members:
            if member.id == BOT_ID:
                # Bot qo'shilganida administratorlarga xabar yuborish
                await bot.send_message(
                    chat_id=ADMINS[0],
                    text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhiga qo'shildi!"
                )
                await db.add_group(group_id=message.chat.id)
            # Yangi a'zo uchun HTML formatida mention
            mention = member.get_mention(name=member.first_name, as_html=True)
            member_mentions.append(mention)

        # Salomlashish xabari
        if member_mentions:
            await message.answer(f"Xush kelibsiz, {' , '.join(member_mentions)}!", parse_mode="HTML")
        else:
            # Agar faqat bot qo'shilmagan bo'lsa, oddiy xush kelibsiz xabarini yuborish
            await message.answer(f"Xush kelibsiz, {message.from_user.full_name}")

        # Xabarni o'chirish
        await message.delete()

    except aiogram.exceptions.MessageCantBeDeleted:
        await alert_message(alert_text="guruhga qo'shilganligi", message=message)


@dp.message_handler(IsGroup(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    try:
        left_member = message.left_chat_member
        if left_member.id == message.from_user.id:
            await message.answer(f"{left_member.get_mention(as_html=True)} guruhni tark etdi")

        else:
            # Admin tomonidan haydalgan foydalanuvchi
            if left_member.id == BOT_ID:
                await bot.send_message(
                    chat_id=ADMINS[0],
                    text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhidan chiqarildi!"
                )
                await db.delete_group(group_id=message.chat.id)
            else:
                await message.answer(f"{left_member.full_name} guruhdan haydaldi "
                                     f"\n\nAdmin: {message.from_user.get_mention(as_html=True)}.")
                # Xabarni o'chirish
                await message.delete()

    except aiogram.exceptions.MessageCantBeDeleted:
        await alert_message(alert_text="guruhdan chiqqanligi", message=message)


@dp.message_handler(IsGroupPhoto(), content_types=types.ContentType.PHOTO, state="*")
async def delete_non_admin_photos(message: types.Message):
    """Admin bo'lmagan foydalanuvchi rasm yuborsa, xabar o'chiriladi."""
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        await message.delete()
        await message.answer(
            f"⚠️ {message.from_user.full_name}, faqat administratorlar rasm yuborishi mumkin!"
        )
