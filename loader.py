from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from utils.blacklist_db import BlacklistDB
from utils.db_api.admins_db import AdminsDB
from utils.db_api.create_tables import Database
from utils.db_api.groups_db import GroupsDB
from utils.db_api.referrals_db import ReferralsDB
from utils.db_api.users_db import UsersDB

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()
udb = UsersDB(db)
refdb = ReferralsDB(db)
admdb = AdminsDB(db)
blstdb = BlacklistDB(db)
grpdb = GroupsDB(db)
