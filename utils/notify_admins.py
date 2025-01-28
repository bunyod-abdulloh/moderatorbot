from aiogram import Dispatcher

from data.config import ADMIN_GROUP_ID
from utils.user_functions import logging_text


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(ADMIN_GROUP_ID, "Bot ishga tushdi")

    except Exception as err:
        await logging_text(err)
