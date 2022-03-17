import discord
from connection import *


async def get_pre(message, message2 = None):
  if(message2 != None):
    message = message2
  connection, cursor = await get_conn()
  await cursor.execute("SELECT guild_prefix FROM guilds WHERE guild_id = ?", (message.guild.id, ))
  result = await cursor.fetchone()
  await close_conn(connection, cursor)
  return result[0]
