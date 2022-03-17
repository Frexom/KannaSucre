import aiosqlite3

async def get_conn(path):
  conn = await aiosqlite3.connect(path, timeout = 10)
  c = await conn.cursor()
  return conn, c


async def close_conn(connection, cursor):
  await cursor.close()
  await connection.close()
