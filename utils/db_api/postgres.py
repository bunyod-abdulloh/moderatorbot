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
                group_id BIGINT NOT NULL UNIQUE
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
        sql_insert = "INSERT INTO users (telegram_id) VALUES ($1)"
        return await self.execute(sql_insert, telegram_id, fetchrow=True)

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

    # =========================== TABLE | GROUPS ===========================
    async def add_group(self, group_id):
        """ Groups jadvaliga yangi ma'lumotlar qo'shuvchi funksiya """
        sql_insert = " INSERT INTO groups(group_id) VALUES($1) ON CONFLICT(group_id) DO NOTHING"
        group = await self.execute(sql_insert, group_id, fetchrow=True)
        if not group:
            sql_select = "SELECT id FROM groups WHERE group_id=$1"
            group = await self.execute(sql_select, group_id, fetchrow=True)
        return group

    async def get_groups(self):
        """ Guruhni ID siga ko'ra ajratib oluvchi funksiya """
        sql = "SELECT group_id FROM groups"
        return await self.execute(sql, fetch=True)

    async def get_group(self, group_id):
        """ Guruhni ID siga ko'ra ajratib oluvchi funksiya """
        sql = "SELECT group_id FROM groups WHERE group_id=$1"
        return await self.execute(sql, group_id, fetchval=True)

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
