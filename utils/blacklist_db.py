from utils.db_api.create_tables import Database


class BlacklistDB:
    def __init__(self, db: Database):
        self.db = db

    # =========================== TABLE | STATUS_GROUPS ===========================
    # Ushbu jadval botni guruhda ishlashiga cheklov qo'yish uchun ishlatiladi, agar guruh id siga False
    # berilgan bo'lsa, bot o'sha guruhda ishlamaydi!!!
    async def add_group_to_blacklist(self, group_id):
        sql = "INSERT INTO blacklist (group_id) VALUES($1) ON CONFLICT (group_id) DO NOTHING"
        return await self.db.execute(sql, group_id, fetchrow=True)

    async def get_group_by_blacklist(self, group_id):
        sql = "SELECT NOT EXISTS(SELECT 1 FROM blacklist WHERE group_id = $1)"
        return await self.db.execute(sql, group_id, fetchval=True)

    async def delete_group_from_blacklist(self, group_id):
        await self.db.execute("DELETE FROM blacklist WHERE group_id=$1", group_id, execute=True)

    async def drop_table_status_groups(self):
        await self.db.execute("DROP TABLE blacklist", execute=True)