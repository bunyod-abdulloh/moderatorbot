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
            """
        ]
        # Execute each table creation query
        for query in queries:
            await self.execute(query, execute=True)

    async def add_user(self, telegram_id):
        """Add a user to the users table."""
        sql_insert = """
        INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING RETURNING id
        """
        user = await self.execute(sql_insert, telegram_id, fetchrow=True)
        if not user:
            sql_select = "SELECT id FROM users WHERE telegram_id=$1"
            user = await self.execute(sql_select, telegram_id, fetchrow=True)
        return user

    async def add_group(self, group_id):
        """Add a group to the groups table."""
        sql_insert = """
        INSERT INTO groups (group_id) VALUES ($1) ON CONFLICT (group_id) DO NOTHING RETURNING id
        """
        group = await self.execute(sql_insert, group_id, fetchrow=True)
        if not group:
            sql_select = "SELECT id FROM groups WHERE group_id=$1"
            group = await self.execute(sql_select, group_id, fetchrow=True)
        return group

    async def get_group(self, group_id):
        """Get a group by its ID."""
        sql = "SELECT group_id FROM groups WHERE group_id=$1"
        return await self.execute(sql, group_id, fetchrow=True)

    async def delete_group(self, group_id):
        await self.execute("DELETE FROM groups WHERE group_id=$1", group_id, execute=True)

    async def drop_table_groups(self):
        await self.execute("DROP TABLE groups", execute=True)
