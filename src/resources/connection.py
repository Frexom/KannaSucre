import sqlite3

import aiosqlite3


async def getReadingConn():
    conn = await aiosqlite3.connect("src/resources/database/bot.db", timeout=10)
    c = await conn.cursor()
    return conn, c


async def closeConn(connection, cursor):
    await cursor.close()
    await connection.close()


def getStaticReadingConn():
    conn = sqlite3.connect("src/resources/database/bot.db", timeout=10)
    c = conn.cursor()
    return conn, c


def closeStaticConn(connection, cursor):
    cursor.close()
    connection.close()
