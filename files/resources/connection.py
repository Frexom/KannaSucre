import aiosqlite3
import sqlite3

async def get_conn(path):
  conn = await aiosqlite3.connect(path, timeout = 10)
  c = await conn.cursor()
  return conn, c


async def close_conn(connection, cursor):
  await cursor.close()
  await connection.close()


def get_static_conn(path):
    conn = sqlite3.connect(path, timeout = 10)
    c = conn.cursor()
    return conn, c

def close_static_conn(connection, cursor):
    cursor.close()
    connection.close()
