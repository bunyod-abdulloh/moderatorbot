from typing import List

from aiogram import types

from loader import dp


@dp.message_handler(is_media_group=True, content_types=['any'])
async def mediagr(message: types.Message, album: List[types.Message]):
    media_group = types.MediaGroup()

    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id
        try:
            media_group.attach({"media": file_id,
                                "type": obj.content_type,
                                "caption": obj.caption})
        except Exception:
            return await message.answer("Xatolik!")
    await message.answer_media_group(media=media_group)
