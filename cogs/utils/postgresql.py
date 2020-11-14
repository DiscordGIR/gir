import asyncpg

class Database:
    async def init(self):
        self.conn = await asyncpg.connect(
            host     = "127.0.0.1",
            database = "botty",
            user     = "emy"
        )

    async def get(self, table):
        stmt = await self.conn.prepare(f'SELECT * FROM {table}')
        return await stmt.fetch()