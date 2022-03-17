import discord
from discord.ext import commands
from connection import *
from prefix import *
import asyncio


import sys
sys.path.append("./ressources")


async def welcome_channel_setup(bot, ctx):
  author = ctx.message.author
  channel = ctx.channel

  def check(m):
    return m.channel == channel and m.author == author


  await ctx.send("Please mention the welcome channel, where you want new members to be greeted! (input 0 if you want to disable it)")
  success = 0
  fail_counter = 0
  while success == 0 and fail_counter < 3:
    try:
      msg = await bot.wait_for('message',  check=check, timeout = 10)
      connection, cursor = await get_conn("./files/ressources/bot.db")
      if len(msg.channel_mentions) > 0:
        channel = msg.channel_mentions[0].id
        await cursor.execute("UPDATE guilds SET guild_welcome_channel_ID = ? WHERE guild_id=?",(channel, ctx.guild.id))
        success = 1
      elif str(msg.content) == str(0):
        await cursor.execute("UPDATE guilds SET guild_welcome_channel_ID = ? WHERE guild_id=?",(0, ctx.guild.id))
        success = 1
      else:
        await ctx.send("Incorrect answer, please try again.")
        fail_counter += 1;
      await connection.commit()
      await close_conn(connection, cursor)
    except asyncio.TimeoutError:
      fail_counter += 10
      await ctx.send("Command timed out, please try again.")
  if success == 1:
   await msg.add_reaction("\u2705")
   return 1
  return 0



async def announcement_channel_setup(bot, ctx):
  author = ctx.message.author
  channel = ctx.channel

  def check(m):
    return m.channel == channel and m.author == author


  await ctx.send("Please mention the announcements channel, where you want to receive the latest KannaSucre's news! (input 0 if you want to disable it)")
  success = 0
  fail_counter = 0
  while success == 0 and fail_counter < 3:
    try:
      msg = await bot.wait_for('message',  check=check, timeout = 10)
      connection, cursor = await get_conn("./files/ressources/bot.db")
      if len(msg.channel_mentions) > 0:
        channel = msg.channel_mentions[0].id
        await cursor.execute("UPDATE guilds SET guild_announcements_channel_ID = ? WHERE guild_id=?",(channel, ctx.guild.id))
        success = 1
      elif str(msg.content) == str(0):
        await cursor.execute("UPDATE guilds SET guild_announcements_channel_ID = ? WHERE guild_id=?",(0, ctx.guild.id))
        success = 1
      else:
        await ctx.send("Incorrect answer, please try again.")
        fail_counter += 1;
      await connection.commit()
      await close_conn(connection, cursor)

    except asyncio.TimeoutError:
      fail_counter += 10
      await ctx.send("Command timed out, please try again.")
  if success == 1:
   await msg.add_reaction("\u2705")
   return 1
  return 0



async def prefix_setup(bot, ctx):
  author = ctx.message.author
  channel = ctx.channel

  def check(m):
    return m.channel == channel and m.author == author


  await ctx.send("Please input the bot's prefix you wish to use on this server. (default is `!`)")
  success = 0

  try:
    msg = await bot.wait_for('message',  check=check, timeout = 10)
    prefix = msg.content.split(" ")[0]
    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("UPDATE guilds SET guild_prefix = ? WHERE guild_id=?",(prefix, ctx.guild.id))
    success = 1
    await connection.commit()
    await close_conn(connection, cursor)

  except asyncio.TimeoutError:
    await ctx.send("Command timed out, please try again.")
  if success == 1:
   await msg.add_reaction("\u2705")
   return 1
  return 0



async def setup(bot, ctx):
  if not ctx.author.bot and ctx.author.guild_permissions.manage_guild:
    await ctx.send("Welcome to the KannaSucre's server setup!")
    await asyncio.sleep(2)
    last_func = await prefix_setup(bot, ctx)
    if last_func == 1:
      last_func = await welcome_channel_setup(bot, ctx)
    if last_func == 1:
      last_func = await announcement_channel_setup(bot, ctx)
    if last_func == 1:
      await asyncio.sleep(2)
      await ctx.send("Thanks! This server is now set up!")
  else :
    await missing_perms(ctx, "setup", "manage_server")
