from utils.db_api.create_tables import Database


class UsersDB:
    def __init__(self, db: Database):
        self.db = db

    # =========================== TABLE | USERS ===========================
    async def add_user(self, telegram_id):
        """ Add a user to the private table. """
        sql = "INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING"
        return await self.db.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.db.execute(sql, fetchval=True)

    async def select_all_users(self):
        sql = "SELECT telegram_id FROM users "
        return await self.db.execute(sql, fetch=True)

    async def delete_user(self, telegram_id):
        await self.db.execute("DELETE FROM users WHERE telegram_id=$1", telegram_id, execute=True)

    async def drop_table_users(self):
        await self.db.execute("DROP TABLE users", execute=True)
