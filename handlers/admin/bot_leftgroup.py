from aiogram import types
from magic_filter import F

from loader import dp, bot, db


@dp.callback_query_handler(F.data.startswith("leftbot:"))
async def handle_leftbot(call: types.CallbackQuery):
    group_id = int(call.data.split(":")[1])
    await db.update_group_status(False, group_id)
    await call.message.edit_text(text="Guruh uchun bot faoliyati cheklandi!")
