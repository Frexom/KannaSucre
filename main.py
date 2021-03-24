from discord.ext import commands
import discord
import aiosqlite
import os
from PIL import Image, ImageFont, ImageDraw
from random import randint
from discord.utils import get
from asyncio import sleep
from keep_alive import keep_alive


async def get_pre(bot, message):
  connection = await aiosqlite.connect('bot.db')
  c = await connection.cursor()
  await c.execute("SELECT prefix FROM info WHERE Server_ID="+ str(message.guild.id))
  result = await c.fetchone()
  await connection.close()
  return result[0]


default_intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_pre , intents = default_intents)
connection = aiosqlite.connect('bot.db')


async def missing_perms(ctx, command_name: str, perms: str = "Not renseigned"):
  await ctx.channel.send("I'm sorry but you don't meet the requirements to run that command : `"+command_name + "`.\nThis command requires the following permission : `" + perms +"`.")

async def lack_perms(ctx, command_name: str):
  await ctx.channel.send("I'm sorry but the command target has more permissions than you. You can't target them with the following command : `"+command_name + "`.")


@bot.event
async def on_ready():
  game = discord.Game('send "ping" to see prefix')
  await bot.change_presence(status=discord.Status.online, activity=game)
  print("Bot is ready")


@bot.event
async def on_guild_channel_create(channel):
  role = get(channel.guild.roles, name = "Muted")
  await channel.set_permissions(role, send_messages = False, add_reactions = False, speak = False)
    

@bot.event
async def on_member_join(member):
  connection = await aiosqlite.connect('bot.db')
  cursor = await connection.cursor()
  await cursor.execute("SELECT general_channel_ID FROM info WHERE Server_ID=" + str(member.guild.id))
  channel_ID = await cursor.fetchone()
  if channel_ID[0] != 0:
    general: discord.TextChannel = bot.get_channel(channel_ID[0])
    await general.send("<@"+str(member.id)+"> joined the server! Yayy!!")
  if not member.bot:
    await cursor.execute("SELECT member_ID from users where member_ID=" + str(member.id))
    member_ID = await cursor.fetchone()
    if member_ID == None:
      await cursor.execute("INSERT INTO users(member_ID, level, XP) VALUES(?, 0, 0)", (int(member.id),))
      connection.commit()
    connection.close()


@bot.event
async def on_member_remove(member):
  if member.id != 765255086581612575:
    connection = await aiosqlite.connect('bot.db')
    cursor = await connection.cursor()
    await cursor.execute("SELECT general_channel_ID FROM info WHERE Server_ID=" + str(member.guild.id))
    channel_ID = await cursor.fetchone()
    if channel_ID[0] != 0:
      general: discord.TextChannel = bot.get_channel(channel_ID[0])
      await general.send(str(member)+" left the server. :(")


@bot.event
async def on_guild_join(guild):
  connection = await aiosqlite.connect('bot.db')
  cursor = await connection.cursor()
  await cursor.execute("SELECT Server_ID from info WHERE Server_ID =" + str(guild.id))
  if await cursor.fetchone() == None:
    if guild.system_channel != None:
      await cursor.execute("INSERT INTO info(Server_ID, prefix, general_channel_ID) VALUES(?,'!', ?)", (int(guild.id), int(guild.system_channel.id)))
    else:
      await cursor.execute("INSERT INTO info(Server_ID, prefix, general_channel_ID) VALUES(?,'!', ?)", (int(guild.id,), 0))
  for user in guild.members:
    if not user.bot:
      await cursor.execute("SELECT member_ID from users where member_ID="+ str(user.id))
      member_ID = await cursor.fetchone()
      if member_ID == None:
        await cursor.execute("INSERT INTO users(member_ID, level, XP) VALUES(?, 0, 0)", (int(user.id),))
  await connection.commit()
  await connection.close()
  

@bot.event
async def on_message(message):
  if not message.author.bot:
    await get_pre(bot, message)
    if message.content.lower() == "ping":
      await message.channel.send("Pong! Prefix : `" + str(await get_pre(bot, message)) + "`")
    connection = await aiosqlite.connect('bot.db')
    cursor = await connection.cursor()
    await cursor.execute("SELECT LengthLimit FROM info WHERE Server_ID = " + str(message.guild.id))
    limit = await cursor.fetchone()
    if not (type(limit[0]) == type(None)) and len(message.content) > limit[0]:
      print("a")
      await message.author.send("Your message has been deleted since it's too long for the server, try to shorten it down to **" + str(limit[0]) + "** characters.\nHere is your message :\n\n"+str(message.content))
      await message.delete()
    await cursor.execute("SELECT xp, level FROM users WHERE member_ID =" + str(message.author.id))
    user_leveling = await cursor.fetchone()
    print(user_leveling, message.author.name)
    user_xp, user_level = int(user_leveling[0]), int(user_leveling[1])
    user_xp += randint(30,50)
    if user_xp > int(2000*0.25*user_level**2):
      user_level += 1
      user_xp = 1
      await message.channel.send("Congratulations <@"+ str(message.author.id) + ">, you are now level " + str(user_level) + "!")
      await cursor.execute("UPDATE users SET  xp = ?, level = ? WHERE member_ID = ?", (user_xp, user_level, message.author.id))
    else:
      await cursor.execute("UPDATE users SET  xp = ? WHERE member_ID = ?", (user_xp, message.author.id))
    await connection.commit()
    await connection.close()
    await bot.process_commands(message)


@bot.command(name = 'clear')
async def clear(ctx):
  if ctx.message.author.guild_permissions.manage_messages:
    number = ctx.message.content.split(" ")
    if len(number) > 1 and number[1].isdecimal():
      number = int(number[1])
      if number < 51:
        messages = await ctx.channel.history(limit = number + 1).flatten()
        count = -1
        for each in messages:
          await each.delete()
          count += 1
        await ctx.channel.send(str(count)+" messages were deleted :D", delete_after = 5)
      else:
        await ctx.channel.send("You can't clear more than 50 messages at the same time.")
    else:
      prefix = str(await get_pre(bot, ctx))
      await ctx.channel.send("```"+ str(prefix) + "clear *number_of_messages*```")
  else:
    await missing_perms(ctx, "clear", "manage messages")

  
@bot.command(name = "kick")
async def kick(ctx):
  if ctx.message.author.guild_permissions.kick_members:
    if len(ctx.message.mentions) > 0:
      if ctx.message.mentions[0].guild_permissions.is_strict_subset(ctx.message.author.guild_permissions):
        reason = ctx.message.content.split(" ")
        reason = ' '.join(reason[2:])
        member = ctx.message.mentions[0]
        if reason != "":
          await member.send("you have been kicked from **" + str(ctx.guild.name) + "**.\nReason : `" + reason + "`.")
        else:
          await member.send("You have been kicked from **" + str(ctx.guild.name) + "**.\nNo reason given.")
        await member.kick()
      else:
        await lack_perms(ctx, "kick")
    else:
      prefix = str(await get_pre(bot, ctx))
      await ctx.channel.send("```"+ str(prefix) + "kick *mention_target*```")
  else:
    await missing_perms(ctx, "kick", "kick members")


@bot.command(name = 'ban')
async def ban(ctx):
  if ctx.message.author.guild_permissions.ban_members:
    if len(ctx.message.mentions) > 0:
      if ctx.message.mentions[0].guild_permissions.is_strict_subset(ctx.message.author.guild_permissions):
        reason = ctx.message.content.split(" ")
        reason = ' '.join(reason[2:])
        member = ctx.message.mentions[0]
        if reason != "":
          await member.send("you have been banned from **" + str(ctx.guild.name) + "**.\nReason : `" + reason + "`.")
        else:
          await member.send("You have been banned from **" + str(ctx.guild.name) + "**.\nNo reason given.")
        await member.ban()
      else:
        await lack_perms(ctx, "ban")
    else:
      prefix = str(await get_pre(bot, ctx))
      await ctx.channel.send("```"+ str(prefix) + "ban *mention_target*```")
  else:
    await missing_perms(ctx, "ban", "ban members")


@bot.command(name = 'prefix')
async def prefix(ctx):
  if ctx.message.author.guild_permissions.manage_guild:
    prefix = ctx.message.content.split(" ")[1]
    connection = await aiosqlite.connect('bot.db')
    cursor = await connection.cursor()
    await cursor.execute("UPDATE info SET prefix = ? WHERE Server_ID=?", (prefix, ctx.guild.id))
    await ctx.channel.send("My prefix for this server now is `" + str(prefix) + "` :)")
    await connection.commit()
    await connection.close()
  else:
    await missing_perms(ctx, "prefix", "manage guild")


@bot.command(name = 'hug')
async def hug(ctx, hugList):
  hugList = ["https://media1.tenor.com/images/89272929c73eefcca4b5f0ec8fe30316/tenor.gif","https://media1.tenor.com/images/1f44c379b43bc4efb6d227a2e20b6b50/tenor.gif","https://images-ext-1.discordapp.net/external/z1Qpvvs0jTvOCec0o_DCD7sU78QC3iT36SnX9EgOPEY/%3Fitemid%3D17730757/https/media1.tenor.com/images/3be3bf592e86d05c89367054a41ff827/tenor.gif","https://images-ext-1.discordapp.net/external/eysfKhUmPR2mbZvLeztQApTxHuKYK69wN-J_wNqQd4s/%3Fitemid%3D15793132https%3A%2F%2Fmedia1.tenor.com%2Fimages%2F7fd514d641f597ac0748c04e47a88d2e%2Ftenor.gif%3Fitemid%3D15793132/https/media1.tenor.com/images/7fd514d641f597ac0748c04e47a88d2e/tenor.gif","https://images-ext-1.discordapp.net/external/xZBEqIadMz71rwKo8VjOCLM9U2qoa5ecw9_T-K7_QdA/%3Fitemid%3D5950582/https/media1.tenor.com/images/96ba07b09e81f9cec49e14a18ba6f701/tenor.gif","https://images-ext-2.discordapp.net/external/cCaEjMcviogmY3aIM0Tt1O_pt4FIRKGA2RrONd-bkww/%3Fitemid%3D14837114/https/media1.tenor.com/images/53916bb4116361f65f9649fd73f366b1/tenor.gif","https://media1.tenor.com/images/f77f9b5c2b20592135431e8a1d536d25/tenor.gif","https://images-ext-2.discordapp.net/external/D8HwdbQ9gjBS5YJnILN8eHXnI1RjfdCMvrcu875ALcU/%3Fitemid%3D17731947/https/media1.tenor.com/images/8727180629ffd5b91ae5674ab264b98f/tenor.gif","https://images-ext-2.discordapp.net/external/tRosj_eohSEf6jbPTcAp0RTY9DfFwpg3tmNogHevFy0/%3Fitemid%3D5680708/https/media1.tenor.com/images/65913379d468b61cd6eb6337c394dccb/tenor.gif","https://images-ext-1.discordapp.net/external/TDmTVkLYuUF2JHH1MTVVUmy8K8EqBoREL2zFJJCt4jA/%3Fitemid%3D13883173/https/media1.tenor.com/images/3c7a770da649c31628f60696962cefca/tenor.gif","https://images-ext-2.discordapp.net/external/AcyEgRazC8yGg71BDrSNvve4qL6nQNp9DHYnP3d--Fw/%3Fitemid%3D9469908/https/media1.tenor.com/images/567fa5edc9aa36dc8b8b00e02b25a352/tenor.gif","https://images-ext-2.discordapp.net/external/PeE1dkLkpyFP18LAXukZCgVoyIHRkOEsKUqzizwWum0/%3Fitemid%3D17584778/https/media1.tenor.com/images/6398ebd19b8f7907a6a16b63e78de7a5/tenor.gif","https://images-ext-1.discordapp.net/external/KJCVyu02jhCZtxuRKIqBH4d3bUWFruRrkCi6DOT1WvI/%3Fitemid%3D14916283/https/media1.tenor.com/images/c715ff7b4fcb2edabd198cedd14d1016/tenor.gif","https://images-ext-1.discordapp.net/external/l61p6wTavtc8jdJsd06_201UeroKhf0C8u8KwdK00DM/%3Fitemid%3D5324255/https/media1.tenor.com/images/c00119443474a031024af2e299947cb8/tenor.gif","https://images-ext-1.discordapp.net/external/ZojPlwyvQiqBkW4ZcuRjwXNzxihEjhohTJ0gl_jMX44/%3Fitemid%3D7992213/https/media1.tenor.com/images/35e8def510afb07b2f7813f6db2047da/tenor.gif","https://images-ext-2.discordapp.net/external/TMoEi3-QXGVFhij85MbmpSevHYcmJ9MVC3iI9Sd2Bpw/%3Fitemid%3D4944125/https/media1.tenor.com/images/159577058f86a9cf6faeed7e3141f5bc/tenor.gif","https://images-ext-2.discordapp.net/external/dzPVkmC21Trw5fHHLZkQtjD0-V5DXdO-66JC-NFnM28/%3Fitemid%3D16843221/https/media1.tenor.com/images/75f007f2541a2d8581b2558af7190714/tenor.gif","https://images-ext-2.discordapp.net/external/n04k5Cp3E1va5CfBtK6yVw4-8MoZQT1UWyXNTufkapE/%3Fitemid%3D17622299/https/media1.tenor.com/images/e960bd971a80f2d97aff1aa16df84663/tenor.gif","https://images-ext-1.discordapp.net/external/wrPKqJpZ8zA1lvRVRBReA9eXjW1wXrdVbxYEw0bTqHQ/%3Fitemid%3D15575523/https/media1.tenor.com/images/e57ae19196e9ce618e21e0fd87985afc/tenor.gif","https://images-ext-1.discordapp.net/external/MPx_UppCsstiEPGzil1N9HsWQnzEdIPXubS95-7-KzE/%3Fitemid%3D16980741/https/media1.tenor.com/images/86a20dbf1dacf6a539569057e20eaeaf/tenor.gif","https://images-ext-2.discordapp.net/external/0EIJruOSuC9KQgbYoOOEQypnv7nvUwOKm2gJjBmgnPo/%3Fitemid%3D7189175/https/media1.tenor.com/images/f64f4e0d22303666d9548623292f0139/tenor.gif","https://images-ext-2.discordapp.net/external/z22EfQQmogLMMuuLPdRaln5LJMTHQ-2M0oF8v--EZY8/%3Fitemid%3D18996997/https/media1.tenor.com/images/1b532e3c2000ac2c4fb3ce033f3a7ccd/tenor.gif","https://images-ext-1.discordapp.net/external/08wWnGRGm65gVFBY557g6knFqNUh_toMu3VHIs-k_G4/%3Fitemid%3D14066854/https/media1.tenor.com/images/1cd2bbd72c77495229f0ff3551b1678f/tenor.gif","https://images-ext-2.discordapp.net/external/MMnPqKTRN4bmkwYZFHrB_xP3vFFKGBKOu4qfd8QcIxs/%3Fitemid%3D15261239/https/media1.tenor.com/images/1b27c69585088b0e99e7007029401852/tenor.gif","https://images-ext-2.discordapp.net/external/XU2wm8ou561yqinnuP2LsNakwTSS19Unzw4m7Lwn3oE/%3Fitemid%3D10592083/https/media1.tenor.com/images/11b756289eec236b3cd8522986bc23dd/tenor.gif","https://images-ext-2.discordapp.net/external/TKLjf4fh-gPUGz5rqi43wvQsOEuYdQE8t252ohpV2ac/%3Fitemid%3D17897599/https/media1.tenor.com/images/8fd2c922b1bcbbe4ca9705d3f18f52b5/tenor.gif","https://images-ext-2.discordapp.net/external/h83u76OvnriZ7afvqZ1fCz6dJUFkD8KBKTQDYfA6Vas/%3Fitemid%3D19371759/https/media1.tenor.com/images/f5e919bfd6afb6b2053bd938443fc2e9/tenor.gif","https://images-ext-2.discordapp.net/external/mkgfJLKSyEBM4WEKn1rSDgvPZVixWX3oRXSlGdaVWNM/%3Fitemid%3D9136391/https/media1.tenor.com/images/b87f8b1e2732c534a00937ffb24baa79/tenor.gif","https://images-ext-2.discordapp.net/external/C6SiaGIvPgKsqVV3x3t1OJXek2u11U1Qneplum0aoxE/%3Fitemid%3D17789653/https/media1.tenor.com/images/99622a9f154d4147abaf5d3599e01ff9/tenor.gif","https://images-ext-2.discordapp.net/external/_iucgRsucqeB_vceyHC34iNdT4_BcH74GARjBhm0TbE/%3Fitemid%3D12070724/https/media1.tenor.com/images/8503ea13c80b50a0ed9320bdf317f925/tenor.gif","https://images-ext-2.discordapp.net/external/pKEEV4dnDAId2EVxdcNhNOzHGSP25as_yybQ17cKGFc/%3Fitemid%3D15150359/https/media1.tenor.com/images/31f85fdb5dde1c383de6ada6540b2020/tenor.gif","https://images-ext-1.discordapp.net/external/9bGqfmZg3CZP1kYnrNIG1k3MUpMcGvTRQiT54gCPaEY/%3Fitemid%3D14844150/https/media1.tenor.com/images/205cde7485168c9d7aac25106a80eece/tenor.gif","https://images-ext-2.discordapp.net/external/NBc-nqT40aiCKGpT0IJupvnU7pIuAIsevwU8D3xdyt4/%3Fitemid%3D14301347/https/media1.tenor.com/images/e00b951f034b08c3c3bf88e7d22aec57/tenor.gif","https://images-ext-1.discordapp.net/external/HwlmE9KbNY0nAJW-7z75ms2tJSNhc6K8PNg5VUq67gE/%3Fitemid%3D17907296/https/media1.tenor.com/images/1a8fdd0d554f187eea34dec252c8a411/tenor.gif","https://images-ext-1.discordapp.net/external/5LADATezVgnP0Gk5dLdXfgnI1AdTwo9BTOpsoaMh2Ko/%3Fitemid%3D14637016/https/media1.tenor.com/images/4db088cfc73a5ee19968fda53be6b446/tenor.gif","https://images-ext-2.discordapp.net/external/ntTSKfK0BeNy3nAclTl5WeSesdV6zQBvvrpZNaNRG2A/%3Fitemid%3D14246498/https/media1.tenor.com/images/969f0f462e4b7350da543f0231ba94cb/tenor.gif","https://images-ext-1.discordapp.net/external/q5s6oHF9R6FwOHPrUxly-Oi0nO-YUmO7BQrtXl-8CNI/%3Fitemid%3D7552087/https/media1.tenor.com/images/03ff67460b3e97cf13aac5d45a072d22/tenor.gif","https://images-ext-1.discordapp.net/external/2TAL2AoHlWYA2U4lStmtWb8CCo0S417XnedHFaz9uaw/%3Fitemid%3D19674705/https/media1.tenor.com/images/f7b6be96e8ebb23319b43304da0e1118/tenor.gif"]
  if ctx.message.author == ctx.message.mentions[0]:
    e = discord.Embed(title = str(ctx.message.author.name) + ", I see you're lonely, take my hug! :heart:")
    e.set_image(url="https://media1.tenor.com/images/1506349f38bf33760d45bde9b9b263a4/tenor.gif")
  else:  
    e = discord.Embed(title = str(ctx.message.mentions[0].name) + ", you have been hugged by " + str(ctx.message.author.name) + " :heart:")
    e.set_image(url=str(hugList[randint(0,len(hugList)-1)]))
  await ctx.send(embed = e)


@bot.command(name = 'mute')
async def mute(ctx):
  if ctx.message.author.guild_permissions.manage_messages:
    if ctx.message.mentions[0].guild_permissions.is_strict_subset(ctx.message.author.guild_permissions):
      reason = ctx.message.content.split(" ")
      duration = None
      if len(reason) > 2 and reason[2].isdecimal():
        duration = int(reason[2])
        reason = ' '.join(reason[3:])
      elif len(reason) > 2:
        print(reason[2:])
        reason = ' '.join(reason[2:])
      else:
        reason = ""

      if not discord.utils.get(ctx.guild.roles, name = "Muted"):
        perms = discord.Permissions(send_messages = False, add_reactions = False, speak = False)
        await ctx.guild.create_role(name = 'Muted', color = int("d90951", 16), permissions = perms)
        role = get(ctx.guild.roles, name = "Muted")
        for chan in ctx.guild.channels:
          await chan.set_permissions(role, send_messages = False, add_reactions = False, speak = False)
      role = get(ctx.guild.roles, name = "Muted")
      if role not in ctx.message.mentions[0].roles:
        if type(duration) == int:
          DM = "You have been muted on **" + str(ctx.guild.name) +"** for **" + str(duration) + "** minutes."
        else:
          DM = "You have been muted on **" + str(ctx.guild.name) +"** indefintely."
        if reason != "":
          DM += "\nReason : `" + str(reason) + "`."
        await ctx.message.mentions[0].send(DM)
        await ctx.message.mentions[0].add_roles(role)
        if type(duration) == int:
          await sleep(duration*60)
          await ctx.message.mentions[0].remove_roles(role)
          await ctx.message.mentions[0].send("You have been unmuted from **" + str(ctx.guild.name)) + "**."
      else:
        await ctx.channel.send("That user is already muted.")
    else:
      await lack_perms(ctx, "mute")
  else:
    await missing_perms(ctx, "mute", "manage messages")


@bot.command(name = 'unmute')
async def unmute(ctx):
  if ctx.message.author.guild_permissions.manage_messages:
    if ctx.message.mentions[0].guild_permissions.is_strict_subset(ctx.message.author.guild_permissions):
      reason = ctx.message.content.split(" ")
      reason = ' '.join(reason[2:])
      role = discord.utils.get(ctx.guild.roles, name = "Muted")
      if role in ctx.message.mentions[0].roles:
        await ctx.message.mentions[0].remove_roles(role)
        await ctx.message.mentions[0].send("You have been unmuted from " + str(ctx.guild.name) + ".")
        await ctx.message.channel.send(str(ctx.message.mentions[0]) + " has been unmuted.")
      else:
        await ctx.message.channel.send("That user isn't muted.")
    else:
      await lack_perms(ctx, "unmute")
  else:
    await missing_perms(ctx, "unmute", "manage messages")


@bot.command(name = 'general')
async def general(ctx):
  if ctx.message.author.guild_permissions.manage_guild:
    channel = ctx.message.channel_mentions[0].id
    connection = await aiosqlite.connect('bot.db')
    cursor = await connection.cursor()
    await cursor.execute("UPDATE info SET general_channel_ID = ? WHERE Server_ID=?", (channel, ctx.guild.id))
    await ctx.channel.send("The general channel now is <#" + str(channel) + "> :)")
    await connection.commit()
    await connection.close()
  else:
        await missing_perms(ctx, "general", "manage guild")


@bot.command(name = 'level')
async def level(ctx):
  if len(ctx.message.mentions) == 0:
    user = ctx.message.author
  else:
    user = ctx.message.mentions[0]

  connection = await aiosqlite.connect('bot.db')
  cursor = await connection.cursor()
  await cursor.execute("SELECT level, xp FROM users WHERE member_ID = " + str(user.id))
  stats = await cursor.fetchone()
  image = Image.open("LevelCommand/Base.png")
  font = ImageFont.truetype("LevelCommand/coolvetica.ttf", size=40)
  d = ImageDraw.Draw(image)
  location = (100, 50)
  text_color = (200, 200, 200)
  message = str(user.name) + "\nLevel " + str(stats[0]) + "\n" + str(stats[1]) + "/" +str(int(2000*0.25*stats[0]**2)) + "XP"
  d.text(location, message, font=font, fill=text_color)
  image.save("LevelCommand/stats" + str(user.name) + ".png")
  
  await ctx.channel.send(file = discord.File("LevelCommand/stats" + str(user.name) + ".png"))


@bot.command(name = 'lengthlimit')
async def lengthlimit(ctx):
  if ctx.message.author.guild_permissions.manage_guild:
    limit = ctx.message.content.split(" ")[1]
    if limit.isdecimal() and int(limit) > 299:
      connection = await aiosqlite.connect('bot.db')
      cursor = await connection.cursor()
      await cursor.execute("UPDATE info SET LengthLimit = ? WHERE Server_ID=?", (limit, ctx.guild.id))
      await ctx.channel.send("The message character limit for this server now is **" + str(limit) + "** characters :)")
      await connection.commit()
      await connection.close()
    else:
      await ctx.channel.send("I'm sorry but the character limit must be at least 300 characters.")
  else:
    await missing_perms(ctx, "lengthlimit", "manage guild")



keep_alive()
bot.run(os.getenv("TOKEN"))
