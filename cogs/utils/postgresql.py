import asyncpg
import json
import os

class Database:
    async def init(self):
        self.conn = await asyncpg.connect(
            host     = os.environ.get("BOTTY_DBHOST"),
            database = os.environ.get("BOTTY_DB"),
            user     = os.environ.get("BOTTY_DBUSER"),
            password = os.environ.get("BOTTY_DBPASSWORD"),
        )

    async def get(self, table):
        stmt = await self.conn.prepare(f'SELECT * FROM "{table}"')
        return await stmt.fetch()

    async def get_with_id(self, table, _id):
        stmt = await self.conn.prepare(f'SELECT * FROM "{table}" WHERE id = $1')
        return await stmt.fetch(str(_id))

    async def get_with_key(self, table, key):
        stmt = await self.conn.prepare(f'SELECT "{key}" FROM {table}')
        return await stmt.fetch()
        
    async def get_with_key_and_id(self, table, key, _id):
        stmt = await self.conn.prepare(f'SELECT "{key}" FROM {table} WHERE id = $1')
        return await stmt.fetch(str(_id))

    async def append_json(self, table, key, _id, _json):
        _json = str(json.dumps(_json))
        await self.conn.execute(f'INSERT INTO "{table}" (id, {key}) VALUES($2, array[$1::json]) ON CONFLICT (id) DO UPDATE SET {key} = EXCLUDED.{key} || $1::json WHERE EXCLUDED.id = $2', _json, str(_id))

    async def set_with_key_and_id(self, table, key, _id, val):
        await self.conn.execute(f'UPDATE "{table}" SET "{key}" = $1 WHERE id = $2', val, str(_id))

    async def increment_and_get(self, table, key, _id, val):
        return await self.conn.fetch(f'UPDATE "{table}" SET "{key}" = "{key}" + $1 WHERE id = $2 RETURNING *', int(val), str(_id))

    async def rank(self, _id):
        return await self.conn.fetch("SELECT yes.xp_rank FROM (SELECT id, COUNT(users), xp, RANK() OVER (ORDER BY xp DESC) xp_rank FROM users GROUP BY id) AS yes WHERE id = $1;", str(_id))