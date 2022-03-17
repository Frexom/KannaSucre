import discord
import aiosqlite3
import os
import random
import sys
sys.path.append("./files")
sys.path.append("./files/ressources")

from discord.ext import commands
from dotenv import load_dotenv

from connection import *
from prefix import *

from owner import *
from admin import *
from setup import *
from moderation import *
from utilities import *
from image_editing import *
from fun import *
from poke import *



default_intents = discord.Intents.default()
bot = commands.Bot(command_prefix=get_pre, intents=default_intents)
bot.remove_command('help')

load_dotenv()


@bot.event
async def on_ready():
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
  connection, cursor = await get_conn("./files/ressources/bot.db")
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
  connection, cursor = await get_conn("./files/ressources/bot.db")
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
  connection, cursor = await get_conn("./files/ressources/bot.db")
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
    prefix = await get_pre(message)
    if message.content.lower() == "ping":
      await message.channel.send("Pong! `" + str(int(bot.latency * 1000)) + "ms`\nPrefix : `" + prefix + "`")
    connection, cursor = await get_conn("./files/ressources/bot.db")
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


@bot.command(name = "preview")
@commands.is_owner()
async def previewCommand(ctx):
    await preview(ctx)

@bot.command(name = "announce")
@commands.is_owner()
async def announceCommand(ctx):
    await annnounce(bot, ctx)

@bot.command(name = "sql")
@commands.is_owner()
async def sqlCommand(ctx):
    await sql(bot, ctx)

@bot.command(name = "database")
@commands.is_owner()
async def databaseCommand(ctx):
    await database(ctx)

@bot.command(name = "shutdown")
@commands.is_owner()
async def shutdownCommand(ctx):
    await shutdown(bot, ctx)

@bot.command(name = "prefix")
async def prefixCommand(ctx):
    await prefix(ctx)

@bot.command(name = "ban")
async def banCommand(ctx):
    await ban(ctx)

@bot.command(name = "welcome")
async def welcomeCommand(ctx):
    await welcome(ctx)

@bot.command(name = "announcements")
async def announcementsCommand(ctx):
    await announcements(ctx)

@bot.command(name = "lengthlimit")
async def lengthlimitCommand(ctx):
    await lengthlimit(ctx)

@bot.command(name = "setup")
async def setupCommand(ctx):
    await setup(bot, ctx)

@bot.command(name = "clear")
async def clearCommand(ctx):
    await clear(ctx)

@bot.command(name = "prune")
async def pruneCommand(ctx):
    await prune(ctx)

@bot.command(name = "kick")
async def kickCommand(ctx):
    await kick(ctx)

@bot.command(name = "dice")
async def diceCommand(ctx):
    await dice(ctx)

@bot.command(name = "servericon")
async def servericonCommand(ctx):
    await servericon(ctx)

@bot.command(name = "usericon")
async def usericonCommand(ctx):
    await usericon(ctx)

@bot.command(name = "help")
async def helpCommand(ctx):
    await help(ctx)

@bot.command(name = "level")
async def levelCommand(ctx):
    await level(ctx)

@bot.command(name = "hug")
async def hugCommand(ctx):
    await hug(ctx)

@bot.command(name = "stand")
async def standCommand(ctx):
    await stand(ctx)

@bot.command(name = "poke")
async def pokeCommand(ctx):
    await poke(bot, ctx)

@bot.command(name = "pokeinfo")
async def pokeinfoCommand(ctx):
    await pokeinfo(bot, ctx)

@bot.command(name = "rolls")
async def rollsCommand(ctx):
    await rolls(ctx)

@bot.command(name = "pokedex")
async def pokedexCommand(ctx):
    await pokedex(bot, ctx)

@bot.command(name = "pokerank")
async def pokerankCommand(ctx):
    await pokerank(bot, ctx)


bot.run(os.environ['TOKEN'])
