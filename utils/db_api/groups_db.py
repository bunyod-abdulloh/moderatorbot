from utils.db_api.create_tables import Database


class GroupsDB:
    def __init__(self, db: Database):
        self.db = db

    # =========================== TABLE | GROUPS ===========================
    async def add_group(self, group_id, telegram_id):
        """Groups jadvaliga yangi ma'lumotlar qo'shuvchi funksiya"""
        sql = "INSERT INTO groups(group_, user_id) VALUES($1, $2) ON CONFLICT (group_) DO NOTHING"
        await self.db.execute(sql, group_id, telegram_id, execute=True)

    async def update_add_user(self, users, group_id):
        sql = "UPDATE groups SET users = $1 WHERE group_ = $2"
        return await self.db.execute(sql, users, group_id, execute=True)

    async def update_group_id(self, new_group_id, old_group_id):
        sql = "UPDATE groups SET group_ = $1 WHERE group_ = $2"
        return await self.db.execute(sql, new_group_id, old_group_id, execute=True)

    async def get_groups(self):
        sql = "SELECT * FROM groups"
        return await self.db.execute(sql, fetch=True)

    async def get_group(self, group_id):
        sql = "SELECT * FROM groups WHERE group_ = $1"
        return await self.db.execute(sql, group_id, fetchrow=True)

    async def get_group_by_user(self, telegram_id):
        sql = "SELECT * FROM groups WHERE user_id = $1"
        return await self.db.execute(sql, telegram_id, fetch=True)

    async def delete_group(self, group_id):
        await self.db.execute("DELETE FROM groups WHERE group_ = $1 returning id", group_id, execute=True)

    async def drop_table_groups(self):
        await self.db.execute("DROP TABLE groups CASCADE", execute=True)
