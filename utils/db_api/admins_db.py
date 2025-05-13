from utils.db_api.create_tables import Database


class AdminsDB:
    def __init__(self, db: Database):
        self.db = db

    # =========================== TABLE | SEND_STATUS | BOT ADMINKASI UCHUN ===========================
    async def add_send_status(self):
        sql = ("INSERT INTO send_status (send_post) SELECT false "
               "WHERE NOT EXISTS (SELECT 1 FROM send_status WHERE send_post = false)")
        return await self.db.execute(sql, fetchrow=True)

    async def update_send_status(self, send_post):
        sql = "UPDATE send_status SET send_post = $1"
        return await self.db.execute(sql, send_post, execute=True)

    async def get_send_status(self):
        sql = "SELECT send_post FROM send_status"
        return await self.db.execute(sql, fetchval=True)

    async def drop_table_send_status(self):
        await self.db.execute("DROP TABLE send_status", execute=True)
