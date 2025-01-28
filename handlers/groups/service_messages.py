from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BotKicked

from data.config import ADMINS, BOT_ID
from filters.group_chat import IsGroup, IsGroupAdminOrOwner, IsGroupAndBotAdmin
from loader import dp, bot, db
from utils.user_functions import logging_text


def get_restrict_permissions(can_send: bool):
    return types.ChatPermissions(
        can_send_messages=can_send,
        can_send_media_messages=can_send,
        can_send_other_messages=can_send,
        can_invite_users=True
    )


async def check_bot_status(message: types.Message):
    bot_ = await db.get_group_on_status(message.chat.id)

    if bot_ and not bot_['on_status']:
        await message.answer("Botning faoliyati ushbu guruh uchun cheklangan! Bot adminiga murojaat qiling!")
        await bot.leave_chat(message.chat.id)
        return False
    return True


@dp.message_handler(IsGroupAdminOrOwner(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member_admin(message: types.Message):
    try:
        check_bot = await db.get_group(message.chat.id)

        if check_bot:
            bot_ = await db.get_group_on_status(message.chat.id)

            if bot_ and not bot_['on_status']:
                await message.answer("Botning faoliyati ushbu guruh uchun cheklangan! Bot adminiga murojaat qiling!")
                await bot.leave_chat(message.chat.id)
                return False
            return True

        member_names = [member.first_name for member in message.new_chat_members]

        for member in message.new_chat_members:
            if member.id == BOT_ID:
                await bot.send_message(
                    chat_id=ADMINS[0],
                    text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhiga qo'shildi!"
                )
                id_ = await db.add_group(telegram_id=message.from_user.id, group_id=message.chat.id)

                await db.add_status_group(id_['id'])
                await db.add_send_status()

        await message.answer(f"Xush kelibsiz, {', '.join(member_names)}!", parse_mode="HTML")
        await message.delete()

    except MessageCantBeDeleted:
        await message.answer(
            text="Bot guruhga admin qilinmaganligi sababli foydalanuvchi guruhga qo'shilganligi haqidagi habarni "
                 "o'chirmadi!\n\nBot to'g'ri ishlashi uchun botni guruhga admin qilishingiz lozim!"
        )

    except Exception as err:
        await logging_text(err)


@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    try:
        group = await db.get_group(message.chat.id)
        inviter_id = message.from_user.id
        member_names = [member.first_name for member in message.new_chat_members if not member.is_bot]

        if message.new_chat_members[0].id == inviter_id and group['users'] > 0:
            await message.chat.restrict(inviter_id, permissions=get_restrict_permissions(False))
        else:
            for member in message.new_chat_members:
                if member.is_bot:
                    await message.chat.kick(user_id=member.id)

            if group['users'] > 0:
                user_data = await db.count_users_inviter(inviter_id)

                if user_data is None:
                    quantity = await db.add_user_to_count_users(inviter_id=inviter_id,
                                                                quantity=len(message.new_chat_members))
                else:
                    quantity = await db.update_quantity(quantity=len(message.new_chat_members), inviter_id=inviter_id)

                if quantity >= group['users']:
                    await message.chat.restrict(user_id=inviter_id, permissions=get_restrict_permissions(True))
                    await db.delete_from_count_user(inviter_id=inviter_id)

        await message.answer(f"Xush kelibsiz, {', '.join(member_names)}!", parse_mode="HTML")
        await message.delete()

    except Exception as err:
        await logging_text(err)


@dp.message_handler(IsGroup(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    try:
        if await IsGroupAndBotAdmin().check(message):
            await message.delete()

    except BotKicked:
        await bot.send_message(
            chat_id=ADMINS[0],
            text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhidan chiqarildi!"
        )
        await db.delete_group(group_id=message.chat.id)

    except Exception as err:
        await logging_text(err)
