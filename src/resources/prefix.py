import discord

from src.resources.connection import *


async def get_pre(message, message2=None):
    if message2 != None:
        message = message2

    if message.guild is not None:
        connection, cursor = await getReadingConn()
        await cursor.execute(
            "SELECT guild_prefix FROM dis_guild WHERE guild_id = ?", (message.guild.id,)
        )
        result = await cursor.fetchone()
        await closeConn(connection, cursor)
        return result[0]
    else:
        return "!"
