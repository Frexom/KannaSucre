import aiosqlite3
import sqlite3

async def getReadingConn(path):
  conn = await aiosqlite3.connect(path, timeout = 10)
  c = await conn.cursor()
  return conn, c


async def closeConn(connection, cursor):
  await cursor.close()
  await connection.close()


def getStaticReadingConn(path):
    conn = sqlite3.connect(path, timeout = 10)
    c = conn.cursor()
    return conn, c

def closeStaticConn(connection, cursor):
    cursor.close()
    connection.close()
