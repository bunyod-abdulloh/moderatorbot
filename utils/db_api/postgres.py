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
            CREATE TABLE IF NOT EXISTS count_users (                
                inviter_id BIGINT NOT NULL UNIQUE,
                quantity INTEGER NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS groups (                
                telegram_id BIGINT NULL,
                group_id BIGINT NOT NULL,
                users INTEGER DEFAULT 0,
                created_at DATE DEFAULT CURRENT_DATE,
                status BOOLEAN DEFAULT TRUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS send_status (
                id SERIAL PRIMARY KEY,
                send_post BOOLEAN DEFAULT FALSE
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
    async def add_user_to_count_users(self, inviter_id, quantity):
        """ Add a user to the private table. """
        sql = "INSERT INTO count_users (inviter_id, quantity) VALUES ($1, $2) returning quantity"
        return await self.execute(sql, inviter_id, quantity, fetchval=True)

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
    async def add_group(self, telegram_id, group_id):
        """ Groups jadvaliga yangi ma'lumotlar qo'shuvchi funksiya """
        sql = " INSERT INTO groups(telegram_id, group_id) VALUES($1, $2)"
        group = await self.execute(sql, telegram_id, group_id, fetchrow=True)
        if not group:
            sql_select = "SELECT * FROM groups WHERE group_id=$1"
            group = await self.execute(sql_select, group_id, fetchrow=True)
        return group

    async def update_add_user(self, users, group_id):
        sql = "UPDATE groups SET users = $1 WHERE group_id = $2"
        return await self.execute(sql, users, group_id, execute=True)

    async def update_group_status(self, status, group_id):
        sql = "UPDATE groups SET status = $1 WHERE group_id = $2"
        return await self.execute(sql, status, group_id, execute=True)

    async def get_groups(self):
        sql = "SELECT * FROM groups"
        return await self.execute(sql, fetch=True)

    async def get_group(self, group_id, status=False):
        sql = "SELECT * FROM groups WHERE group_id=$1"
        if status:
            return await self.execute(sql, group_id, fetchrow=True)
        else:
            return await self.execute(sql, group_id, fetch=True)

    async def get_group_by_user(self, telegram_id):
        sql = "SELECT * FROM groups WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetch=True)

    async def delete_group(self, group_id):
        await self.execute("DELETE FROM groups WHERE group_id=$1", group_id, execute=True)

    async def drop_table_groups(self):
        await self.execute("DROP TABLE groups", execute=True)

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
