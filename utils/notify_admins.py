from aiogram import Dispatcher

from services.error_service import notify_exception_to_admin


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(1041847396, "Bot ishga tushdi")

    except Exception as err:
        await notify_exception_to_admin(err=err)
