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
                users INTEGER DEFAULT 0                
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS count_users (
                group_id BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,                
                inviter_id BIGINT NOT NULL UNIQUE,
                quantity INTEGER DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS status_groups (                
                created_at DATE DEFAULT CURRENT_DATE,                
                group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE, 
                on_status BOOLEAN DEFAULT TRUE                
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
        sql = "INSERT INTO count_users (group_id, inviter_id, quantity) VALUES ($1, $2, $3) returning quantity"
        return await self.execute(sql, group_id, inviter_id, quantity, fetchval=True)

    async def update_quantity(self, quantity, inviter_id):
        sql = "UPDATE count_users SET quantity = quantity + $1 WHERE inviter_id = $2 returning quantity"
        return await self.execute(sql, quantity, inviter_id, fetchval=True)

    async def count_users_inviter(self, inviter_id):
        sql = "SELECT quantity FROM count_users WHERE inviter_id=$1"
        return await self.execute(sql, inviter_id, fetchval=True)

    async def delete_from_count_user(self, inviter_id):
        await self.execute("DELETE FROM count_users WHERE inviter_id=$1", inviter_id, execute=True)

    async def drop_table_count_users(self):
        await self.execute("DROP TABLE count_users", execute=True)

    # =========================== TABLE | GROUPS ===========================
    async def add_group(self, group_id, telegram_id):
        """ Groups jadvaliga yangi ma'lumotlar qo'shuvchi funksiya """
        sql = " INSERT INTO groups(group_, user_id) VALUES($1, $2) returning id"
        group = await self.execute(sql, group_id, telegram_id, fetchrow=True)
        if not group:
            sql_select = "SELECT * FROM groups WHERE group_ = $1"
            group = await self.execute(sql_select, group_id, fetchrow=True)
        return group

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
    async def add_status_group(self, group_id):
        sql = "INSERT INTO status_groups (group_id) VALUES ($1)"
        return await self.execute(sql, group_id, fetchrow=True)

    async def update_group_on_status(self, status, group_id):
        sql = "UPDATE status_groups SET on_status = $1 WHERE group_id = $2"
        return await self.execute(sql, status, group_id, execute=True)

    async def get_group_on_status(self, group_id):
        query = (
            "SELECT sg.group_id, sg.created_at, sg.on_status, g.user_id, g.group_ AS "
            "group_identifier FROM status_groups sg JOIN groups g ON sg.group_id = g.id WHERE g.group_ = $1")
        return await self.execute(query, group_id, fetchrow=True)

    async def drop_table_status_groups(self):
        await self.execute("DROP TABLE status_groups", execute=True)

    # =========================== TABLE | SEND_STATUS ===========================
    async def add_send_status(self):
        sql = "INSERT INTO send_status (send_post) VALUES (false)"
        return await self.execute(sql, fetchrow=True)

    async def update_send_status(self, send_post):
        sql = "UPDATE send_status SET send_post = $1"
        return await self.execute(sql, send_post, execute=True)

    async def get_send_status(self):
        sql = "SELECT send_post FROM send_status"
        return await self.execute(sql, fetchval=True)

    async def drop_table_send_status(self):
        await self.execute("DROP TABLE send_status", execute=True)

    async def delete_table_by_name(self, table_name, group_id):
        await self.execute(f"DELETE FROM {table_name} WHERE group_id = $1", group_id, fetchval=True)

    # =========================== TABLE | REFERRAL ===========================
    async def add_referral(self, name):
        sql = "INSERT INTO referrals (name) VALUES ($1)"
        return await self.execute(sql, name, fetchrow=True)

    async def add_user_referral(self, name, user_id):
        sql = "INSERT INTO referrals (name, user_id, amount) VALUES ($1, $2, 1) ON CONFLICT (user_id) DO NOTHING"
        return await self.execute(sql, name, user_id, fetchrow=True)

    async def update_referral(self, name):
        sql = "UPDATE referrals SET amount = amount + 1, created_at = current_date WHERE name = $1"
        return await self.execute(sql, name, execute=True)

    async def get_referral_by_id(self, id_):
        sql = ("SELECT r.*, agg.total_amount FROM referrals r LEFT JOIN (SELECT name, SUM(amount) AS "
               "total_amount FROM referrals GROUP BY name) agg ON r.name = agg.name WHERE r.id = $1")
        return await self.execute(sql, id_, fetchrow=True)

    async def get_today_referrals(self):
        sql = ("SELECT name, SUM(amount) AS total_invites FROM referrals WHERE created_at = CURRENT_DATE GROUP BY name "
               "ORDER BY MIN(id)")
        return await self.execute(sql, fetch=True)

    async def get_all_referrals(self):
        sql = "SELECT name, id FROM referrals WHERE amount = 0"
        return await self.execute(sql, fetch=True)

    async def delete_referral_by_id(self, id_):
        await self.execute(f"DELETE FROM referrals WHERE id = $1", id_, fetchval=True)

    async def drop_table_referrals(self):
        await self.execute("DROP TABLE referrals", execute=True)
