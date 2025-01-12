from aiogram import types
from aiogram.dispatcher.filters import Command
from magic_filter import F

from filters import IsGroupAndBotAdmin
from filters.group_chat import is_admin
from loader import dp, bot


@dp.message_handler(IsGroupAndBotAdmin(), Command("restrict_media"))
async def restrict_media_messages(message: types.Message):
    if await is_admin(bot, message.chat.id, message.from_user.id):
        await bot.set_chat_permissions(
            chat_id=message.chat.id,
            permissions=types.ChatPermissions(
                can_send_messages=True,
                can_send_audios=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_voice_messages=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_documents=False,
                can_send_polls=False
            )
        )

