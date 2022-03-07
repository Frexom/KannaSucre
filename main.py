from discord.ext import commands
import discord
import aiosqlite3
import time
import os
import random
import asyncio
from PIL import Image, ImageFont, ImageDraw
from dotenv import load_dotenv




async def get_pre(bot, message):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT guild_prefix FROM guilds WHERE guild_id = ?", (message.guild.id, ))
  result = await cursor.fetchone()
  await close_conn(connection, cursor)
  return result[0]



default_intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_pre, intents=default_intents)
bot.remove_command('help')

load_dotenv()




async def get_conn():
  conn = await aiosqlite3.connect("bot.db", timeout = 10)
  c = await conn.cursor()
  return conn, c


async def close_conn(connection, cursor):
  await cursor.close()
  await connection.close()



async def create_global_pokecount():
  connection, cursor = await get_conn()
  await cursor.execute("SELECT COUNT(*) FROM pokedex")
  global poke_count
  temp = await cursor.fetchone()
  poke_count = temp[0]
  await close_conn(connection, cursor)


async def missing_perms(ctx, command_name: str, perms: str = "Not renseigned"):
  await ctx.send("I'm sorry but you don't meet the requirements to run that command : `" + command_name + "`.\nThis command requires the following permission : `" + perms + "`.")


async def lack_perms(ctx, command_name: str):
  await ctx.send("I'm sorry but the command target has as much as or more permissions than you. You can't target them with the following command : `" + command_name + "`.")


def get_target(ctx):
  if len(ctx.message.mentions) > 0:
    return ctx.message.mentions[0]
  return ctx.message.author


def get_mention(ctx):
  if len(ctx.message.mentions) > 0:
    return ctx.message.mentions[0]
  return None




@bot.event
async def on_ready():
  await create_global_pokecount()
  for i in range(len(bot.guilds)):
    await setup_func(bot.guilds[i])
  game = discord.Game('send "ping" to see prefix')
  await bot.change_presence(status=discord.Status.online, activity=game)
  random.seed(time.time())
  print("Bot is ready")



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error



async def setup_func(guild) :
  connection, cursor = await get_conn()
  await cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild.id, ))
  if await cursor.fetchone() == None:
    await cursor.execute("INSERT INTO guilds(guild_id, guild_prefix) VALUES(?, '!')", (guild.id, ))
  for user in guild.members :
    if not user.bot:
      await cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id, ))
      if await cursor.fetchone() == None:
        await cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user.id, ))
  await connection.commit()
  await close_conn(connection, cursor)



@bot.event
async def on_member_join(member):
  connection, cursor = await get_conn()
  await cursor.execute( "SELECT guild_welcome_channel_id FROM guilds WHERE guild_id = ?", (member.guild.id,))
  channel_ID = await cursor.fetchone()
  channel_ID = channel_ID[0]
  if channel_ID != 0:
    welcome_channel: discord.TextChannel = bot.get_channel(channel_ID)
    await welcome_channel.send("<@" + str(member.id) + "> joined the server! Yayy!!")

  if not member.bot:
    await cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (member.id, ))
    member_id = await cursor.fetchone()
    if member_id == None:
      await cursor.execute("INSERT INTO users(user_id) VALUES(?)", (int(member.id), ))
      await connection.commit()
  await close_conn(connection, cursor)



@bot.event
async def on_member_remove(member):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT guild_welcome_channel_ID FROM guilds WHERE guild_id = ?", (member.guild.id, ))
  channel_ID = await cursor.fetchone()
  if channel_ID[0] != 0:
    welcome_channel: discord.TextChannel = bot.get_channel(channel_ID[0])
    await welcome_channel.send(str(member) + " left the server. :(")
  await close_conn(connection, cursor)



@bot.event
async def on_guild_join(guild):
  await setup_func(guild)



@bot.event
async def on_message(message):
  if not message.author.bot :
    prefix = await get_pre(bot, message)
    if message.content.lower() == "ping":
      await message.channel.send("Pong! `" + str(int(bot.latency * 1000)) + "ms`\nPrefix : `" + prefix + "`")
    connection, cursor = await get_conn()
    await cursor.execute("SELECT guild_lengthlimit FROM guilds WHERE guild_id = ?", (message.guild.id, ))
    limit = await cursor.fetchone()
    if limit[0] != None and len(message.content) > limit[0] :
      await message.author.send("Your message has been deleted since it's too long for the server, try to short it down to **" + str(limit[0]) + "** characters.\nHere is your message :\n\n" + str(message.content))
      await message.delete()
    await cursor.execute("SELECT user_xp, user_level FROM users WHERE user_id = ?", (message.author.id, ))
    user_leveling = await cursor.fetchone()
    user_xp = user_leveling[0]
    user_level = user_leveling[1]
    user_xp += random.randint(30,50)
    if user_xp > 500*user_level:
      user_xp -= 500*user_level
      user_level +=1
      await cursor.execute("UPDATE users SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, message.author.id))
      await message.channel.send("Congratulations <@" + str(message.author.id) + ">, you are now level " + str(user_level) + "!")
    else:
      await cursor.execute("UPDATE users SET user_xp = ? WHERE user_id = ?", (user_xp, message.author.id))
    await connection.commit()
    await close_conn(connection, cursor)
    await bot.process_commands(message)



@bot.command(name='clear')
async def clear(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_messages:
      number = ctx.message.content.split(" ")
      if len(number) > 1 and number[1].isdecimal():
        number = int(number[1]) +1
        if number < 52:
          mess_count = len(await ctx.channel.purge(limit = number))
          await ctx.send(str(mess_count-1) + " messages were deleted :D", delete_after=5)
        else:
          await ctx.send("You can't clear more than 50 messages at the same time.")
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) + "clear *number of messages*```")
    else:
      await missing_perms(ctx, "clear", "manage messages")



@bot.command(name='prune')
async def prune(ctx):
  if not ctx.message.author.bot :
    await ctx.channel.trigger_typing()
    if ctx.message.author.guild_permissions.manage_messages:
      user = get_mention(ctx)
      if user is not None:
        if not user.guild_permissions.manage_messages or user.bot:
          def checkUser(m):
            return m.author == user
          mess_count = 0
          for channel in ctx.guild.text_channels:
            mess_count += len(await channel.purge(limit = 200, check = checkUser))
          message = str(mess_count) + " messages from `" + user.name + "` were deleted on `" + ctx.guild.name + "`."
          await ctx.send(message, delete_after=5)
          await ctx.author.send(message)
        else:
          await lack_perms(ctx, "prune")
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) + "prune *mention targeted user*```")
    else:
      await missing_perms(ctx, "prune", "manage messages")



@bot.command(name="kick")
async def kick(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.kick_members:
      reason = ctx.message.content.split(" ")
      if len(ctx.message.mentions) > 0 or (len(reason) > 1 and reason[1].isdecimal() and len(reason[1]) > 15):
        if reason[1].isdecimal():
          member = ctx.guild.get_member(int(reason[1]))
        else:
          member = ctx.message.mentions[0]
        reason = ' '.join(reason[2:])
        if not member.guild_permissions.kick_members:
          if not member.bot:
            if reason != "":
              await member.send("you have been kicked from **" + str(ctx.guild.name) + "**.\nReason : `" + reason + "`.")
            else:
              await member.send("You have been kicked from **" + str(ctx.guild.name) + "**.\nNo reason given.")
          await member.kick()
          await ctx.message.add_reaction("\u2705")
        else:
         await lack_perms(ctx, "kick")
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) + "kick *mention target/target ID*```")
    else:
      await missing_perms(ctx, "kick", "kick members")



@bot.command(name='ban')
async def ban(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.ban_members:
      reason = ctx.message.content.split(" ")
      if len(ctx.message.mentions) > 0 or (len(reason) > 1 and reason[1].isdecimal() and len(reason[1]) > 15):
        if reason[1].isdecimal():
          member = ctx.guild.get_member(int(reason[1]))
        else:
          member = ctx.message.mentions[0]
        if not member.guild_permissions.ban_members:
          reason = ' '.join(reason[2:])
          if not member.bot:
            if reason != "":
              await member.send("you have been banned from **" + str(ctx.guild.name) + "**.\nReason : `" + reason + "`.")
            else:
              await member.send("You have been banned from **" + str(ctx.guild.name) + "**.\nNo reason given.")
          await member.ban()
          await ctx.message.add_reaction("\u2705")
        else:
          await lack_perms(ctx, "ban")
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) + "ban *mention target/target ID* *reason(optional)*```")
    else:
        await missing_perms(ctx, "ban", "ban members")



@bot.command(name='prefix')
async def prefix(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      prefix = ctx.message.content.split(" ")
      if len(prefix) > 1:
        prefix = prefix[1]
        connection, cursor = await get_conn()
        await cursor.execute("UPDATE guilds SET guild_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        await ctx.send("My prefix for this server now is `" + str(prefix) + "` :)")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) + "prefix *new prefix*```")
    else:
      await missing_perms(ctx, "prefix", "manage guild")



@bot.command(name='hug')
async def hug(ctx):
  if not ctx.message.author.bot :
    if len(ctx.message.mentions) > 0:
      hugList = [
            "https://media1.tenor.com/images/89272929c73eefcca4b5f0ec8fe30316/tenor.gif",
            "https://media1.tenor.com/images/1f44c379b43bc4efb6d227a2e20b6b50/tenor.gif",
            "https://images-ext-1.discordapp.net/external/z1Qpvvs0jTvOCec0o_DCD7sU78QC3iT36SnX9EgOPEY/%3Fitemid%3D17730757/https/media1.tenor.com/images/3be3bf592e86d05c89367054a41ff827/tenor.gif",
            "https://images-ext-1.discordapp.net/external/eysfKhUmPR2mbZvLeztQApTxHuKYK69wN-J_wNqQd4s/%3Fitemid%3D15793132https%3A%2F%2Fmedia1.tenor.com%2Fimages%2F7fd514d641f597ac0748c04e47a88d2e%2Ftenor.gif%3Fitemid%3D15793132/https/media1.tenor.com/images/7fd514d641f597ac0748c04e47a88d2e/tenor.gif",
            "https://images-ext-1.discordapp.net/external/xZBEqIadMz71rwKo8VjOCLM9U2qoa5ecw9_T-K7_QdA/%3Fitemid%3D5950582/https/media1.tenor.com/images/96ba07b09e81f9cec49e14a18ba6f701/tenor.gif",
            "https://images-ext-2.discordapp.net/external/cCaEjMcviogmY3aIM0Tt1O_pt4FIRKGA2RrONd-bkww/%3Fitemid%3D14837114/https/media1.tenor.com/images/53916bb4116361f65f9649fd73f366b1/tenor.gif",
            "https://media1.tenor.com/images/f77f9b5c2b20592135431e8a1d536d25/tenor.gif",
            "https://images-ext-2.discordapp.net/external/D8HwdbQ9gjBS5YJnILN8eHXnI1RjfdCMvrcu875ALcU/%3Fitemid%3D17731947/https/media1.tenor.com/images/8727180629ffd5b91ae5674ab264b98f/tenor.gif",
            "https://images-ext-2.discordapp.net/external/tRosj_eohSEf6jbPTcAp0RTY9DfFwpg3tmNogHevFy0/%3Fitemid%3D5680708/https/media1.tenor.com/images/65913379d468b61cd6eb6337c394dccb/tenor.gif",
            "https://images-ext-1.discordapp.net/external/TDmTVkLYuUF2JHH1MTVVUmy8K8EqBoREL2zFJJCt4jA/%3Fitemid%3D13883173/https/media1.tenor.com/images/3c7a770da649c31628f60696962cefca/tenor.gif",
            "https://images-ext-2.discordapp.net/external/AcyEgRazC8yGg71BDrSNvve4qL6nQNp9DHYnP3d--Fw/%3Fitemid%3D9469908/https/media1.tenor.com/images/567fa5edc9aa36dc8b8b00e02b25a352/tenor.gif",
            "https://images-ext-2.discordapp.net/external/PeE1dkLkpyFP18LAXukZCgVoyIHRkOEsKUqzizwWum0/%3Fitemid%3D17584778/https/media1.tenor.com/images/6398ebd19b8f7907a6a16b63e78de7a5/tenor.gif",
            "https://images-ext-1.discordapp.net/external/KJCVyu02jhCZtxuRKIqBH4d3bUWFruRrkCi6DOT1WvI/%3Fitemid%3D14916283/https/media1.tenor.com/images/c715ff7b4fcb2edabd198cedd14d1016/tenor.gif",
            "https://images-ext-1.discordapp.net/external/l61p6wTavtc8jdJsd06_201UeroKhf0C8u8KwdK00DM/%3Fitemid%3D5324255/https/media1.tenor.com/images/c00119443474a031024af2e299947cb8/tenor.gif",
            "https://images-ext-1.discordapp.net/external/ZojPlwyvQiqBkW4ZcuRjwXNzxihEjhohTJ0gl_jMX44/%3Fitemid%3D7992213/https/media1.tenor.com/images/35e8def510afb07b2f7813f6db2047da/tenor.gif",
            "https://images-ext-2.discordapp.net/external/TMoEi3-QXGVFhij85MbmpSevHYcmJ9MVC3iI9Sd2Bpw/%3Fitemid%3D4944125/https/media1.tenor.com/images/159577058f86a9cf6faeed7e3141f5bc/tenor.gif",
            "https://images-ext-2.discordapp.net/external/dzPVkmC21Trw5fHHLZkQtjD0-V5DXdO-66JC-NFnM28/%3Fitemid%3D16843221/https/media1.tenor.com/images/75f007f2541a2d8581b2558af7190714/tenor.gif",
            "https://images-ext-2.discordapp.net/external/n04k5Cp3E1va5CfBtK6yVw4-8MoZQT1UWyXNTufkapE/%3Fitemid%3D17622299/https/media1.tenor.com/images/e960bd971a80f2d97aff1aa16df84663/tenor.gif",
            "https://images-ext-1.discordapp.net/external/wrPKqJpZ8zA1lvRVRBReA9eXjW1wXrdVbxYEw0bTqHQ/%3Fitemid%3D15575523/https/media1.tenor.com/images/e57ae19196e9ce618e21e0fd87985afc/tenor.gif",
            "https://images-ext-1.discordapp.net/external/MPx_UppCsstiEPGzil1N9HsWQnzEdIPXubS95-7-KzE/%3Fitemid%3D16980741/https/media1.tenor.com/images/86a20dbf1dacf6a539569057e20eaeaf/tenor.gif",
            "https://images-ext-2.discordapp.net/external/0EIJruOSuC9KQgbYoOOEQypnv7nvUwOKm2gJjBmgnPo/%3Fitemid%3D7189175/https/media1.tenor.com/images/f64f4e0d22303666d9548623292f0139/tenor.gif",
            "https://images-ext-2.discordapp.net/external/z22EfQQmogLMMuuLPdRaln5LJMTHQ-2M0oF8v--EZY8/%3Fitemid%3D18996997/https/media1.tenor.com/images/1b532e3c2000ac2c4fb3ce033f3a7ccd/tenor.gif",
            "https://images-ext-1.discordapp.net/external/08wWnGRGm65gVFBY557g6knFqNUh_toMu3VHIs-k_G4/%3Fitemid%3D14066854/https/media1.tenor.com/images/1cd2bbd72c77495229f0ff3551b1678f/tenor.gif",
            "https://images-ext-2.discordapp.net/external/MMnPqKTRN4bmkwYZFHrB_xP3vFFKGBKOu4qfd8QcIxs/%3Fitemid%3D15261239/https/media1.tenor.com/images/1b27c69585088b0e99e7007029401852/tenor.gif",
            "https://images-ext-2.discordapp.net/external/XU2wm8ou561yqinnuP2LsNakwTSS19Unzw4m7Lwn3oE/%3Fitemid%3D10592083/https/media1.tenor.com/images/11b756289eec236b3cd8522986bc23dd/tenor.gif",
            "https://images-ext-2.discordapp.net/external/TKLjf4fh-gPUGz5rqi43wvQsOEuYdQE8t252ohpV2ac/%3Fitemid%3D17897599/https/media1.tenor.com/images/8fd2c922b1bcbbe4ca9705d3f18f52b5/tenor.gif",
            "https://images-ext-2.discordapp.net/external/h83u76OvnriZ7afvqZ1fCz6dJUFkD8KBKTQDYfA6Vas/%3Fitemid%3D19371759/https/media1.tenor.com/images/f5e919bfd6afb6b2053bd938443fc2e9/tenor.gif",
            "https://images-ext-2.discordapp.net/external/mkgfJLKSyEBM4WEKn1rSDgvPZVixWX3oRXSlGdaVWNM/%3Fitemid%3D9136391/https/media1.tenor.com/images/b87f8b1e2732c534a00937ffb24baa79/tenor.gif",
            "https://images-ext-2.discordapp.net/external/C6SiaGIvPgKsqVV3x3t1OJXek2u11U1Qneplum0aoxE/%3Fitemid%3D17789653/https/media1.tenor.com/images/99622a9f154d4147abaf5d3599e01ff9/tenor.gif",
            "https://images-ext-2.discordapp.net/external/_iucgRsucqeB_vceyHC34iNdT4_BcH74GARjBhm0TbE/%3Fitemid%3D12070724/https/media1.tenor.com/images/8503ea13c80b50a0ed9320bdf317f925/tenor.gif",
            "https://images-ext-2.discordapp.net/external/pKEEV4dnDAId2EVxdcNhNOzHGSP25as_yybQ17cKGFc/%3Fitemid%3D15150359/https/media1.tenor.com/images/31f85fdb5dde1c383de6ada6540b2020/tenor.gif",
            "https://images-ext-1.discordapp.net/external/9bGqfmZg3CZP1kYnrNIG1k3MUpMcGvTRQiT54gCPaEY/%3Fitemid%3D14844150/https/media1.tenor.com/images/205cde7485168c9d7aac25106a80eece/tenor.gif",
            "https://images-ext-2.discordapp.net/external/NBc-nqT40aiCKGpT0IJupvnU7pIuAIsevwU8D3xdyt4/%3Fitemid%3D14301347/https/media1.tenor.com/images/e00b951f034b08c3c3bf88e7d22aec57/tenor.gif",
            "https://images-ext-1.discordapp.net/external/HwlmE9KbNY0nAJW-7z75ms2tJSNhc6K8PNg5VUq67gE/%3Fitemid%3D17907296/https/media1.tenor.com/images/1a8fdd0d554f187eea34dec252c8a411/tenor.gif",
            "https://images-ext-1.discordapp.net/external/5LADATezVgnP0Gk5dLdXfgnI1AdTwo9BTOpsoaMh2Ko/%3Fitemid%3D14637016/https/media1.tenor.com/images/4db088cfc73a5ee19968fda53be6b446/tenor.gif",
            "https://images-ext-2.discordapp.net/external/ntTSKfK0BeNy3nAclTl5WeSesdV6zQBvvrpZNaNRG2A/%3Fitemid%3D14246498/https/media1.tenor.com/images/969f0f462e4b7350da543f0231ba94cb/tenor.gif",
            "https://images-ext-1.discordapp.net/external/q5s6oHF9R6FwOHPrUxly-Oi0nO-YUmO7BQrtXl-8CNI/%3Fitemid%3D7552087/https/media1.tenor.com/images/03ff67460b3e97cf13aac5d45a072d22/tenor.gif",
            "https://images-ext-1.discordapp.net/external/2TAL2AoHlWYA2U4lStmtWb8CCo0S417XnedHFaz9uaw/%3Fitemid%3D19674705/https/media1.tenor.com/images/f7b6be96e8ebb23319b43304da0e1118/tenor.gif"
      ]
      if ctx.message.author == ctx.message.mentions[0]:
        e = discord.Embed(title=str(ctx.message.author.name) + ", I see you're lonely, take my hug! :heart:")
        e.set_image(url="https://media1.tenor.com/images/1506349f38bf33760d45bde9b9b263a4/tenor.gif")
      else:
        e = discord.Embed(title=str(ctx.message.mentions[0].name) + ", you have been hugged by " + str(ctx.message.author.name) + " :heart:")
        e.set_image(url=str(hugList[random.randint(0, len(hugList) - 1)]))
      await ctx.send(embed=e)
    else:
      prefix = str(await get_pre(bot, ctx))
      await ctx.send("```" + str(prefix) + "hug *mention user*```")



@bot.command(name='welcome')
async def welcome(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      connection, cursor = await get_conn()
      message = ctx.message.content.split(" ")
      if len(ctx.message.channel_mentions) > 0 or len(message) > 1 and message[1] == str(0):
        if len(ctx.message.channel_mentions) > 0:
          channel = ctx.message.channel_mentions[0].id
        else:
          channel = 0
        await cursor.execute("UPDATE guilds SET guild_welcome_channel_id = ? WHERE guild_id=?", (channel, ctx.guild.id))
        await ctx.message.add_reaction("\u2705")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        await cursor.execute("SELECT guild_welcome_channel_id FROM guilds WHERE guild_id = ?", (ctx.guild.id, ))
        welcome = await cursor.fetchone()
        await close_conn(connection, cursor)
        welcome = welcome[0]
        prefix = str(await get_pre(bot, ctx))
        if welcome != 0 :
          await ctx.send("The current welcome channel is <#" + str(welcome) + ">. If you want to change it, please use this command :\n" + "```" + str(prefix) + "welcome   *mention new welcome channel or 0 to disable*```")
        else :
          await ctx.send("There is not defined welcome channel defined for this server right now. If you want to set up one to see who enters and leaves your server, please use this command :\n" + "```" + str(prefix) + "welcome *mention new welcome channel*```")
    else:
      await missing_perms(ctx, "welcome", "manage guild")



@bot.command(name='announcements')
async def announcements(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      connection, cursor = await get_conn()
      message = ctx.message.content.split(" ")
      if len(ctx.message.channel_mentions) > 0 or len(message) > 1 and message[1] == str(0):
        if len(ctx.message.channel_mentions) > 0:
          channel = ctx.message.channel_mentions[0].id
        else:
          channel = 0
        await cursor.execute("UPDATE guilds SET guild_announcements_channel_ID = ? WHERE guild_id=?",(channel, ctx.guild.id))
        await ctx.message.add_reaction("\u2705")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        await cursor.execute("SELECT guild_announcements_channel_ID FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
        announcements = await cursor.fetchone()
        await close_conn(connection, cursor)
        announcements = announcements[0]
        prefix = str(await get_pre(bot, ctx))
        if announcements != 0 :
          await ctx.send("The current announcements channel is <#" + str(announcements) + ">. If you want to change it, please use this command :\n" + "```" + str(prefix) +   "announcements *mention new announcements channel or 0 to disable*```")
        else :
          await ctx.send("There is not defined announcements channel defined for this server right now. If you want to set up one to stay tuned with the latest KannaSucre News, please use this command :\n" + "```" + str(prefix) + "announcements *mention new announcements channel*```")
    else:
      await missing_perms(ctx, "announcements", "manage guild")



@bot.command(name="lengthlimit")
async def lengthlimit(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      limit = ctx.message.content.split(" ")
      if len(limit) > 1 and limit[1].isdecimal():
        limit = limit[1]
        if limit.isdecimal() and int(limit) > 299:
          connection, cursor = await get_conn()
          await cursor.execute("UPDATE guilds SET guild_lengthlimit = ? WHERE guild_id = ?",(limit, ctx.guild.id))
          await ctx.send("The message character limit for this server now is **" +str(limit) + "** characters :)")
          await connection.commit()
          await close_conn(connection, cursor)
        else:
          await ctx.send("I'm sorry but the character limit must be at least 300 characters.")
      else:
        prefix = str(await get_pre(bot, ctx))
        await ctx.send("```" + str(prefix) +"lengthlimit *characters limit*```")
    else:
      await missing_perms(ctx, "lengthlimit", "manage guild")



@bot.command(name="dice")
async def dice(ctx):
  if not ctx.message.author.bot :
    words = ctx.message.content.split(" ")
    if len(words) > 1 and words[1].isdecimal() and int(words[1]) > 0:
      i = ctx.message.content.split(" ")[1]
      number = random.randint(1, int(i))
      await ctx.send("Rolled **" + str(number) + "**!")
    else:
      prefix = str(await get_pre(bot, ctx))
      await ctx.send("```" + str(prefix) + "dice *number>0*```")



@bot.command(name="servericon")
async def servericon(ctx):
  if not ctx.message.author.bot:
    await ctx.send(ctx.guild.icon_url or "This server does not have an icon.")



@bot.command(name="usericon")
async def usericon(ctx):
  if not ctx.message.author.bot :
    user = get_target(ctx)
    await ctx.send(user.avatar_url or "This user does not have an icon.")





def get_rarity():
  rand = random.randint(1, 100)
  if rand == 100:
    return [5, "legendary"]
  elif rand >= 95 and rand <= 99:
    return [4, "Super Rare"]
  elif rand >= 80 and rand <=94:
    return [3, "Rare"]
  elif rand >= 55 and rand <=79:
    return [2, "Uncommon"]
  else:
    return [1, "Common"]



def get_shiny():
  rand = random.randint(1, 256)
  if rand == 1:
    return True
  return False




async def get_alt(poke_id):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT DISTINCT pokelink_alt FROM pokelink WHERE poke_id = ?", (poke_id, ))
  alt = await cursor.fetchall()
  await close_conn(connection, cursor)
  if len(alt) == 1:
    return alt[0][0]
  else:
    return alt[random.randint(0, len(alt)-1)][0]


async def get_pokemon_sex(poke_id, poke_alt):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT pokelink_sex FROM pokelink WHERE poke_id = ? AND pokelink_alt = ?", (poke_id, poke_alt))
  data = await cursor.fetchall()
  await close_conn(connection, cursor)
  if len(data) == 1:
    return data[0][0]
  else:
    return data[random.randint(0,len(data)-1)][0]



async def get_pokemon_id(rarity):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT poke_id, poke_name FROM pokedex WHERE poke_rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity, ))
  temp =  await cursor.fetchone()
  await close_conn(connection, cursor)
  return temp



async def get_pokemon_details():
  rarity = get_rarity()
  poke_id = await get_pokemon_id(rarity[0])
  shiny = get_shiny()
  poke_alt = await get_alt(poke_id[0])
  poke_sex = await get_pokemon_sex(poke_id[0], poke_alt)
  connection, cursor = await get_conn()
  if shiny:
    await cursor.execute("SELECT pokelink_shiny FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
  else:
    await cursor.execute("SELECT pokelink_normal FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
  link = await cursor.fetchone()
  await close_conn(connection, cursor)
  try:
    return [poke_id[0], poke_id[1], rarity[0], rarity[1],poke_alt, shiny, poke_sex, link[0]]
  except TypeError:
    owner = bot.get_user(307556664091869185)
    await owner.send(str([poke_id[0], poke_id[1], rarity[0], rarity[1],poke_alt, shiny, poke_sex, link]))
    




@bot.command(name = "poke")
async def poke(ctx):
  if not ctx.message.author.bot :
    await ctx.channel.trigger_typing()
    connection, cursor = await get_conn()
    await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (ctx.message.author.id, ))
    data = await cursor.fetchone()
    last_roll = data[0]
    pity = data[1]
    now = time.time()
    time_since = int(now - last_roll)
    if time_since > 7200 or pity >= 1:
      if time_since < 7200:
        pity -= 1
        await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity, ctx.author.id))
      else:
        await cursor.execute("UPDATE users SET user_last_roll_datetime = ? WHERE user_id = ?", (now, ctx.message.author.id))
      await connection.commit()

      pokemon_details = await get_pokemon_details()

      await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (ctx.message.author.id, pokemon_details[0], pokemon_details[4] ))
      is_obtained = await cursor.fetchone()
      shiny_string = ""
      is_shiny = pokemon_details[5]
      if is_shiny:
        shiny_string = "\nWait!! Is it shiny??? :sparkles:"
      if is_obtained == None:
        await cursor.execute("INSERT INTO pokemon_obtained (user_id, poke_id, pokelink_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (ctx.message.author.id, pokemon_details[0], pokemon_details[4], int(is_shiny), now))
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string
      elif (is_obtained[3] == 0 and is_shiny):
        await cursor.execute("UPDATE pokemon_obtained SET is_shiny = 1 WHERE user_id = ? and poke_id = ?", (ctx.message.author.id, pokemon_details[0]))
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string
      else:
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string + "\nYou already had that pokemon.:confused:\nRolls +" + str(0.25*pokemon_details[2]) + "."
        await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon_details[2], ctx.author.id))
      await connection.commit()
      e = discord.Embed(title = "Congratulation **" + str(ctx.message.author.name) + "**, you got **" + pokemon_details[1] + "**!",  description = desc)
      e.set_image(url=pokemon_details[-1])
      await ctx.send(embed = e)
    else:
      time_left = int(7200 - time_since)
      if time_left > 3600:
        time_left -= 3600
        time_left = int(time_left/60)
        await ctx.send(str(ctx.message.author.name) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
      else:
        time_left += 60
        time_left = int(time_left/60)
        await ctx.send(str(ctx.message.author.name) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
    await close_conn(connection, cursor)



async def get_pokeinfo_embed(poke_id, page, shiny):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT poke_id, poke_name, pokelink_sex, pokelink_normal, pokelink_shiny, poke_desc, pokelink_label FROM pokelink JOIN pokedex USING(poke_id) WHERE poke_id = ?;", (poke_id, ))
  pokedetails = await cursor.fetchall()

  page = page % len(pokedetails)
  poke_sex = ""
  if(pokedetails[page][2] == "f"):
    poke_sex = "\u2640"
  if(pokedetails[page][2] == "m"):
    poke_sex = "\u2642"
  

  if(shiny):
    e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + ":sparkles: " + poke_sex, description = pokedetails[page][6] + " form")
    e.set_image(url=pokedetails[page][4])
  else:
    e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + poke_sex, description = pokedetails[page][6] + " form")
    e.set_image(url=pokedetails[page][3])

  e.add_field(name = "Description : ", value=pokedetails[page][5])
  e.set_footer(text = "page " + str(page+1) + "/" + str(len(pokedetails)))
  return e
    
 


@bot.command(name = "pokeinfo")
async def pokeinfo(ctx):
  if not ctx.author.bot:
    message = ctx.message.content.split(" ")
    if len(message) > 1:
      connection, cursor = await get_conn()
      pokemon = message[1]
      try:
        if not pokemon.isdecimal():
          await cursor.execute("SELECT poke_id FROM pokedex WHERE lower(poke_name) = lower(?)", (pokemon, ))
          poke_id = await cursor.fetchone()
          poke_id = poke_id[0]
        else:
          poke_id = int(message[1])
        if poke_id > poke_count or poke_id <= 0 :
          raise TypeError
        msg = await ctx.send(embed=await get_pokeinfo_embed(poke_id, 0, False))
        await msg.add_reaction(emoji = "\u25C0")
        await msg.add_reaction(emoji = "\u2728")
        await msg.add_reaction(emoji = "\u25B6")
        await asyncio.sleep(1)

        def check(r, a):
          return r.message == msg


        page = 0
        shiny = False
        active = True
        while(active):
          try:
            a = await bot.wait_for("reaction_add", check = check, timeout = 15)
            if a[0].emoji == '▶':
              page = (page + 1)
            elif a[0].emoji == '◀':
              page = (page - 1)
            elif a[0].emoji == '✨':
              shiny = not shiny
                
            await msg.edit(embed=await get_pokeinfo_embed(poke_id, page, shiny))
          except asyncio.TimeoutError:
            active = False
      except TypeError:
        e = discord.Embed(title = "Not found :(", description = "No such pokemon")
        await ctx.send(embed = e)

    else:
      await ctx.channel.send("```" + await get_pre(bot, ctx.message) + "pokeinfo *number/name of pokemon*```")

  else:
    await ctx.send("This command isn't supported for bots.")



@bot.command(name = "rolls")
async def rolls(ctx):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (ctx.message.author.id, ))
  data = await cursor.fetchone()
  last_roll = data[0]
  pity = data[1]
  now = time.time()
  time_since = int(now - last_roll)
  time_left = int(7200 - time_since)
  if time_left <= 0:
    await ctx.send(str(ctx.message.author.name) + ", your poke roll is available.\nRolls : `" + str(pity)+ "`.")
  elif time_left > 3600:
    time_left -= 3600
    time_left = int(time_left/60)
    await ctx.send(str(ctx.message.author.name) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
  else:
    time_left += 60
    time_left = int(time_left/60)
    await ctx.send(str(ctx.message.author.name) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
  await close_conn(connection, cursor)






async def get_pokedex_embed(user, page):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT poke_id, poke_name, is_shiny FROM pokedex JOIN pokemon_obtained USING(poke_id) WHERE user_id = ? ORDER BY poke_id;", (user.id, ))
  Pokemons = await cursor.fetchall()
  await cursor.execute("SELECT COUNT(DISTINCT poke_id) FROM pokemon_obtained WHERE user_id = ?;", (user.id, ))
  number_of_pokemons = await cursor.fetchone()
  number_of_pokemons = number_of_pokemons[0]
  if Pokemons == [] :
    list_pokemons = "No pokemons."
  else:
    list_pokemons = ""
    list_index = 0
    while(Pokemons[list_index][0] <= page*20 and list_index != len(Pokemons)-1) :
      list_index += 1
    for i in range(page*20, page*20+20):
      if i < poke_count:
        if Pokemons[list_index][0] == i+1:
          if Pokemons[list_index][2]:
            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + ":sparkles:\n"
          else:
            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + "\n"
          if list_index < len(Pokemons)-1:
            list_index += 1
        else:
          list_pokemons += str(i+1) + " - --------\n"

  embed=discord.Embed(title = str(user.name) + "'s Pokedex", description = str(number_of_pokemons) + "/" + str(poke_count) + " pokemons")
  embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
  embed.add_field(name="Pokemons :", value=list_pokemons, inline=True)
  embed.set_footer(text = "page " + str(page+1) + "/" + str(int(poke_count/20)+1))
  await close_conn(connection, cursor)
  return embed



@bot.command(name = "pokedex")
async def pokedex(ctx):
  if not ctx.message.author.bot :
    user = get_target(ctx)
    if not user.bot:
      message = ctx.message.content.split(" ")
      page = 0
      if len(message) > 1 and message[1].isdecimal() :
        page = int(message[1])
        page -= 1
        if page < 1 or page > int(poke_count/20)+1:
          page = 0

      msg = await ctx.send(embed=await get_pokedex_embed(user, page))
      await msg.add_reaction(emoji = "\u25C0")
      await msg.add_reaction(emoji = "\u25B6")
      await asyncio.sleep(1)

      def check(r, a):
        return r.message == msg


      active = 1
      while(active == 1):
        try:
          a = await bot.wait_for("reaction_add", check = check, timeout = 15)
          if a[0].emoji == '▶':
            page = (page + 1) % (int(poke_count/20)+1)
          elif a[0].emoji == '◀':
            page = (page - 1) % (int(poke_count/20)+1)
          await msg.edit(embed=await get_pokedex_embed(user, page))
        except asyncio.TimeoutError:
          active = 0


    else:
      await ctx.send("This command isn't supported for bots.")





@bot.command(name = 'announce')
@commands.is_owner()
async def announce(ctx):
  connection, cursor = await get_conn()
  await cursor.execute("SELECT guild_announcements_channel_ID FROM guilds")
  IDs = await cursor.fetchall()
  await close_conn(connection, cursor)
  message_list = ctx.message.content.split(" ")[1:]
  message = ""
  message = " ".join(message_list)
  counter = 0
  for i in range(len(IDs)):
    if IDs[i][0] != 0 and IDs[i][0] != None :
      counter += 1
      channel = bot.get_channel(IDs[i][0])
      await channel.send(message)
  await ctx.send("Announcement made on " + str(counter) + " guilds.")



@bot.command(name = "preview")
@commands.is_owner()
async def preview(ctx):
  message_list = ctx.message.content.split(" ")[1:]
  message = " ".join(message_list)
  await ctx.send(message)



@bot.command(name = "help")
async def help(ctx):
  if not ctx.message.author.bot:
    connection, cursor = await get_conn()
    message_list = ctx.message.content.split(" ")
    if len(message_list) < 2:
      categories = ["__Admin commands :__ \n\n", "\n\n__Moderation commands :__ \n\n", "\n\n__Utilities commands :__ \n\n", "\n\n__Miscellaneous/Fun commands :__ \n\n"]
      await cursor.execute("SELECT com_name, com_short, cat_category FROM commands ORDER BY cat_category, com_name")
      commands = await cursor.fetchall()
      await close_conn(connection, cursor)
      content = ""
      index = 0
      for i in range(4):
        content += categories[i]
        while(index < len(commands) and commands[index][2] == i+1):
          content += "`" + commands[index][0] +  "` : " + commands[index][1] +"\n"
          index += 1;
      embed = discord.Embed(title= "Kannasucre help : ", colour=discord.Colour(0x635f))
      embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
      embed.add_field(name="** **", value=content)
      await ctx.send(embed=embed)
    else:
      await cursor.execute("SELECT com_name, com_desc, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM commands")
      commands = await cursor.fetchall()
      await close_conn(connection, cursor)
      parameter = message_list[1]
      successful = False
      for i in range(len(commands)):
        if commands[i][0] == parameter:
          prefix = str(await get_pre(bot, ctx))
          embed = discord.Embed(title= commands[i][0] + " command :", colour=discord.Colour(0x635f), description=commands[i][1])
          embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
          embed.set_author(name="KannaSucre help,")
          embed.add_field(name="User's perms :      ", value="`" + commands[i][3] + "`", inline = True)
          embed.add_field(name="Kanna's perms :      ", value="`" + commands[i][4] + "`", inline = True)
          if commands[i][5] is not None:
            answer = 'no'
            if int(commands[i][5]) == 1:
              answer = 'yes'
            embed.add_field(name="Does the bot need more perms than target to run that command?", value= "```" + answer + "```", inline = False)
          embed.add_field(name="Example : ", value= "```" + prefix + commands[i][2] + "```", inline = False)
          await ctx.send(embed=embed)
          successful = True
      if successful == False :
        await ctx.send("No command named `" + parameter +"` found.")



@bot.command(name = 'stand')
async def stand(ctx):
  if not ctx.message.author.bot :
    connection, cursor = await get_conn()
    await cursor.execute("SELECT stand_id FROM user_stand WHERE user_id = ?", (ctx.author.id, ))
    stand_id = await cursor.fetchone()
    if stand_id == None:
      stand_id = random.randint(1, 32)
      await cursor.execute("INSERT INTO user_stand(user_id, stand_id) VALUES(?, ?)", (ctx.author.id, stand_id))
    else:
      stand_id = stand_id[0]
    await cursor.execute("SELECT stand_name, stand_link FROM stands WHERE stand_id = ?", (stand_id, ))
    stand = await cursor.fetchone()
    await connection.commit()
    await close_conn(connection, cursor)
    e = discord.Embed(title = ctx.message.author.name + ", your stand is **" + stand[0] + "**.", colour=discord.Colour(0x635f))
    e.set_image(url=stand[1])
    await ctx.send(embed = e)




@bot.command(name = 'sql')
@commands.is_owner()
async def sql(ctx):
  if not ctx.message.author.bot :
    connection, cursor = await get_conn()
    query = ctx.message.content[5:]
    if(query[0].lower() == "s"):
      await cursor.execute(query)
      await ctx.send("That went alright!")
      result = await cursor.fetchall()
      if result == None:
        await ctx.send("None")
      else:
        await ctx.send(result)
    else:
      channel = ctx.channel
      author = ctx.author

      def check(m):
        return m.content == 'y' and m.channel == channel and m.author == author

      await cursor.execute(query)
      await ctx.send(str(cursor.rowcount) + " rows affected.")

      try:
        await ctx.send("Do you want to commit?")
        msg = await bot.wait_for('message',  check=check, timeout = 10)
        if msg:
          await connection.commit()
          await ctx.channel.send("Commited.")

      except asyncio.TimeoutError:
        await ctx.send("Command timed out.")

    await close_conn(connection, cursor)



@bot.command(name = 'pokerank')
async def pokerank(ctx):
  if not ctx.message.author.bot :


    def sort_on_pokemon(e):
      return e[0]


    connection, cursor = await get_conn()
    await cursor.execute("SELECT COUNT(DISTINCT poke_id), user_id FROM pokemon_obtained GROUP BY user_id")
    result = await cursor.fetchall()
    await close_conn(connection, cursor)
    result_list = []
    for i in range(len(result)):
      result_list.append([result[i][0], result[i][1]])
    result_list.sort(reverse=True, key=sort_on_pokemon)
    description = ""
    if len(result_list) < 10:
      limit = len(result_list)
    for i in range(limit):
      user = bot.get_user(result_list[i][1])
      description += str(i+1) + "-" + user.name + " - " + str(result_list[i][0]) + "/" + str(poke_count) + "\n"
    embed=discord.Embed(title= "KannaSucre's Pokerank", colour=discord.Colour(0x635f))
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="Ranking :", value=description)
    await ctx.send(embed=embed)



@bot.command(name = 'level')
async def level(ctx):
  if not ctx.message.author.bot :
    user = get_target(ctx)
    if not user.bot:
      await user.avatar_url_as(format="png").save(fp="LevelCommand/Users/" + str(user.id) + ".png")

      connection, cursor = await get_conn()
      await cursor.execute("SELECT user_level, user_xp FROM users WHERE user_id = ?", (user.id, ))
      stats = await cursor.fetchone()
      await close_conn(connection, cursor)

      image = Image.open("LevelCommand/Base.png")
      ProfilePic = Image.open("LevelCommand/Users/" + str(user.id) + ".png")
      ProfilePic = ProfilePic.resize((190, 190))
      mask_im = Image.new("L", ProfilePic.size, 0)
      draw = ImageDraw.Draw(mask_im)
      draw.ellipse((0, 0, 190, 190), fill=255)
      image.paste(ProfilePic, (556, 30), mask_im)

      if stats[0]>=20:
        bronze = Image.open("LevelCommand/KannaBronze.png")
        mask_im = Image.new("L", bronze.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 49, 49), fill=255)
        image.paste(bronze, (350, 52), mask_im)

        if stats[0]>=50:
          silver = Image.open("LevelCommand/KannaSilver.png")
          image.paste(silver, (405, 52), mask_im)
          if stats[0]>=100:
            gold = Image.open("LevelCommand/KannaGold.png")
            image.paste(gold, (460, 52), mask_im)

      font = ImageFont.truetype("LevelCommand/coolvetica.ttf", size=40)
      d = ImageDraw.Draw(image)
      message = str(user.name) + "\nLevel " + str(stats[0]) + "\n" + str(stats[1]) + "/" +str(500*stats[0]) + "XP"
      d.text((100, 50), message, font=font, fill= (90,90,90))
      image.save("LevelCommand/stats" + str(user.id) + ".png")
      await ctx.send(file = discord.File("LevelCommand/stats" + str(user.id) + ".png"))
    else:
      await ctx.send("This command isn't supported for bots.")





async def welcome_channel_setup(ctx):
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
      connection, cursor = await get_conn()
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



async def announcement_channel_setup(ctx):
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
      connection, cursor = await get_conn()
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



async def prefix_setup(ctx):
  author = ctx.message.author
  channel = ctx.channel

  def check(m):
    return m.channel == channel and m.author == author


  await ctx.send("Please input the bot's prefix you wish to use on this server. (default is `!`)")
  success = 0

  try:
    msg = await bot.wait_for('message',  check=check, timeout = 10)
    prefix = msg.content.split(" ")[0]
    connection, cursor = await get_conn()
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



@bot.command(name = 'setup')
async def setup(ctx):
  if not ctx.author.bot and ctx.author.guild_permissions.manage_guild:
    await ctx.send("Welcome to the KannaSucre's server setup!")
    await asyncio.sleep(2)
    last_func = await prefix_setup(ctx)
    if last_func == 1:
      last_func = await welcome_channel_setup(ctx)
    if last_func == 1:
      last_func = await announcement_channel_setup(ctx)
    if last_func == 1:
      await asyncio.sleep(2)
      await ctx.send("Thanks! This server is now set up!")
  else :
    await missing_perms(ctx, "setup", "manage_server")





@bot.command(name = 'database')
@commands.is_owner()
async def database(ctx):
  await ctx.send(file=discord.File('bot.db'), delete_after=2)



@bot.command(name = 'shutdown')
@commands.is_owner()
async def shutdown(ctx):

  author = ctx.message.author
  channel = ctx.channel
  def check(m):
    return m.content == 'y' and m.channel == channel and m.author == author

  await ctx.send("Do you really want to shut down the bot?")
  try:
    msg = await bot.wait_for('message',  check=check, timeout = 5)
    if msg:
      await ctx.send("Shutting down...")
      print("Shutting down...")
      await asyncio.sleep(1)
      await bot.close()

  except asyncio.TimeoutError:
    await ctx.send("The bot did not shut down.(timeout)")





bot.run(os.environ['TOKEN'])
