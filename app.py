from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from middlewares.media_group import AlbumMiddleware
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    await db.create()
    # await db.drop_table_groups()
    # await db.drop_table_users()
    await db.create_tables()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
