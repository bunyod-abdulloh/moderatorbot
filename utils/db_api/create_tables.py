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
                return None

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
