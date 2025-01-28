import logging
import traceback

from aiogram import Dispatcher

from data.config import ADMIN_GROUP_ID
from utils.user_functions import logging_text


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(ADMIN_GROUP_ID, "Bot ishga tushdi")

    except Exception as err:
        logging.error(f"Xatolik: {err}")
        logging.error("Traceback:\n" + traceback.format_exc())
        error_text = f"Xatolik:\n{err}\n\nTraceback:\n" + traceback.format_exc()
        await dp.bot.send_message(
            chat_id=ADMIN_GROUP_ID, text=error_text
        )
