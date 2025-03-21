from typing import Union

import asyncpg
from asyncpg import Connection, Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        """Create the connection pool for database."""
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(self, command, *args, fetch=False, fetchval=False, fetchrow=False, execute=False):
        """Execute database commands."""
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    return await connection.fetch(command, *args)
                elif fetchval:
                    return await connection.fetchval(command, *args)
                elif fetchrow:
                    return await connection.fetchrow(command, *args)
                elif execute:
                    return await connection.execute(command, *args)

    async def create_tables(self):
        """Create the required tables in the database."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS groups (                
                id SERIAL PRIMARY KEY,
                group_ BIGINT NOT NULL UNIQUE,
                user_id BIGINT NOT NULL,
                users INTEGER DEFAULT 0,
                created_at DATE DEFAULT CURRENT_DATE                
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS count_users (
                group_id BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,                
                inviter_id BIGINT NOT NULL,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (group_id, inviter_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS blacklist (                                
                group_id BIGINT PRIMARY KEY                                
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS send_status (                
                send_post BOOLEAN DEFAULT FALSE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS referrals (                
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                user_id BIGINT NULL UNIQUE,
                created_at DATE DEFAULT CURRENT_DATE,
                amount INTEGER DEFAULT 0  
            );
            """
        ]
        # Execute each table creation query
        for query in queries:
            await self.execute(query, execute=True)

    # =========================== TABLE | USERS ===========================
    async def add_user(self, telegram_id):
        """ Add a user to the private table. """
        sql = "INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def select_all_users(self):
        sql = "SELECT telegram_id FROM users "
        return await self.execute(sql, fetch=True)

    async def delete_user(self, telegram_id):
        await self.execute("DELETE FROM users WHERE telegram_id=$1", telegram_id, execute=True)

    async def drop_table_users(self):
        await self.execute("DROP TABLE users", execute=True)

    # =========================== TABLE | COUNT_USERS ===========================
    async def add_user_to_count_users(self, group_id, inviter_id, quantity):
        """ Add a user to the private table. """
        sql = ("INSERT INTO count_users (group_id, inviter_id, quantity) VALUES ($1, $2, $3) "
               "ON CONFLICT (group_id, inviter_id) DO UPDATE SET quantity = count_users.quantity + EXCLUDED.quantity "
               "RETURNING quantity")
        return await self.execute(sql, group_id, inviter_id, quantity, fetchval=True)

    async def update_quantity(self, quantity, inviter_id, group_id):
        sql = ("UPDATE count_users SET quantity = quantity + $1 WHERE inviter_id = $2 AND group_id = $3 "
               "returning quantity")
        return await self.execute(sql, quantity, inviter_id, group_id, fetchval=True)

    async def count_users_inviter(self, inviter_id):
        sql = "SELECT quantity FROM count_users WHERE inviter_id=$1"
        return await self.execute(sql, inviter_id, fetchval=True)

    async def delete_from_count_user(self, inviter_id):
        await self.execute("DELETE FROM count_users WHERE inviter_id=$1", inviter_id, execute=True)

    async def drop_table_count_users(self):
        await self.execute("DROP TABLE count_users", execute=True)

    # =========================== TABLE | GROUPS ===========================
    async def add_group(self, group_id, telegram_id):
        """Groups jadvaliga yangi ma'lumotlar qo'shuvchi funksiya"""
        sql = "INSERT INTO groups(group_, user_id) VALUES($1, $2) ON CONFLICT (group_) DO NOTHING"
        await self.execute(sql, group_id, telegram_id, execute=True)

    async def update_add_user(self, users, group_id):
        sql = "UPDATE groups SET users = $1 WHERE group_ = $2"
        return await self.execute(sql, users, group_id, execute=True)

    async def update_group_id(self, new_group_id, old_group_id):
        sql = "UPDATE groups SET group_ = $1 WHERE group_ = $2"
        return await self.execute(sql, new_group_id, old_group_id, execute=True)

    async def get_groups(self):
        sql = "SELECT * FROM groups"
        return await self.execute(sql, fetch=True)

    async def get_group(self, group_id):
        sql = "SELECT * FROM groups WHERE group_ = $1"
        return await self.execute(sql, group_id, fetchrow=True)

    async def get_group_by_user(self, telegram_id):
        sql = "SELECT * FROM groups WHERE user_id = $1"
        return await self.execute(sql, telegram_id, fetch=True)

    async def delete_group(self, group_id):
        await self.execute("DELETE FROM groups WHERE group_ = $1 returning id", group_id, execute=True)

    async def drop_table_groups(self):
        await self.execute("DROP TABLE groups CASCADE", execute=True)

    # =========================== TABLE | STATUS_GROUPS ===========================
    # Ushbu jadval botni guruhda ishlashiga cheklov qo'yish uchun ishlatiladi, agar guruh id siga False
    # berilgan bo'lsa, bot o'sha guruhda ishlamaydi!!!
    async def add_group_to_blacklist(self, group_id):
        sql = "INSERT INTO blacklist (group_id) VALUES($1) ON CONFLICT (group_id) DO NOTHING"
        return await self.execute(sql, group_id, fetchrow=True)

    async def get_group_by_blacklist(self, group_id):
        sql = "SELECT NOT EXISTS(SELECT 1 FROM blacklist WHERE group_id = $1)"
        return await self.execute(sql, group_id, fetchval=True)

    async def delete_group_from_blacklist(self, group_id):
        await self.execute("DELETE FROM blacklist WHERE group_id=$1", group_id, execute=True)

    async def drop_table_status_groups(self):
        await self.execute("DROP TABLE blacklist", execute=True)

    # =========================== TABLE | SEND_STATUS | BOT ADMINKASI UCHUN ===========================
    async def add_send_status(self):
        sql = ("INSERT INTO send_status (send_post) SELECT false "
               "WHERE NOT EXISTS (SELECT 1 FROM send_status WHERE send_post = false)")
        return await self.execute(sql, fetchrow=True)

    async def update_send_status(self, send_post):
        sql = "UPDATE send_status SET send_post = $1"
        return await self.execute(sql, send_post, execute=True)

    async def get_send_status(self):
        sql = "SELECT send_post FROM send_status"
        return await self.execute(sql, fetchval=True)

    async def drop_table_send_status(self):
        await self.execute("DROP TABLE send_status", execute=True)

    # =========================== TABLE | REFERRAL ===========================
    async def add_referral(self, name):
        sql = "INSERT INTO referrals (name) SELECT $1::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM referrals WHERE name = $1)"
        return await self.execute(sql, name, execute=True)

    async def add_user_referral(self, name, user_id):
        sql = "INSERT INTO referrals (name, user_id, amount) VALUES ($1, $2, 1) ON CONFLICT (user_id) DO NOTHING"
        return await self.execute(sql, name, user_id, fetchrow=True)

    async def get_referral_by_id(self, id_):
        sql = ("SELECT r.*, agg.total_amount FROM referrals r LEFT JOIN (SELECT name, SUM(amount) AS "
               "total_amount FROM referrals GROUP BY name) agg ON r.name = agg.name WHERE r.id = $1")
        return await self.execute(sql, id_, fetchrow=True)

    async def get_yesterday_referrals(self):
        sql = ("SELECT name, SUM(amount) AS total_invites FROM referrals "
               "WHERE created_at = CURRENT_DATE - INTERVAL '1 day' GROUP BY name ORDER BY MIN(id)")
        return await self.execute(sql, fetch=True)

    async def get_all_referrals(self):
        sql = "SELECT name, id FROM referrals WHERE amount = 0"
        return await self.execute(sql, fetch=True)

    async def delete_referral_by_id(self, id_):
        await self.execute(f"DELETE FROM referrals WHERE id = $1", id_, fetchval=True)

    async def drop_table_referrals(self):
        await self.execute("DROP TABLE referrals", execute=True)
