from utils.db_api.create_tables import Database


class ReferralsDB:
    def __init__(self, db: Database):
        self.db = db

    # =========================== TABLE | REFERRAL ===========================
    async def add_referral(self, name):
        sql = "INSERT INTO referrals (name) SELECT $1::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM referrals WHERE name = $1)"
        return await self.db.execute(sql, name, execute=True)

    async def add_user_referral(self, name, user_id):
        sql = "INSERT INTO referrals (name, user_id, amount) VALUES ($1, $2, 1) ON CONFLICT (user_id) DO NOTHING"
        return await self.db.execute(sql, name, user_id, fetchrow=True)

    async def get_referral_by_id(self, id_):
        sql = ("SELECT r.*, agg.total_amount FROM referrals r LEFT JOIN (SELECT name, SUM(amount) AS "
               "total_amount FROM referrals GROUP BY name) agg ON r.name = agg.name WHERE r.id = $1")
        return await self.db.execute(sql, id_, fetchrow=True)

    async def get_yesterday_referrals(self):
        sql = ("SELECT name, SUM(amount) AS total_invites FROM referrals "
               "WHERE created_at = CURRENT_DATE - INTERVAL '1 day' GROUP BY name ORDER BY MIN(id)")
        return await self.db.execute(sql, fetch=True)

    async def get_all_referrals(self):
        sql = "SELECT name, id FROM referrals WHERE amount = 0"
        return await self.db.execute(sql, fetch=True)

    async def delete_referral_by_id(self, id_):
        await self.db.execute(f"DELETE FROM referrals WHERE id = $1", id_, fetchval=True)

    async def drop_table_referrals(self):
        await self.db.execute("DROP TABLE referrals", execute=True)
