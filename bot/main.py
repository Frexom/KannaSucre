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


from events import *
from owner import *
from admin import *
from setup import *
from moderation import *
from utilities import *
from image_editing import *
from fun import *
from poke import *




default_intents = discord.Intents.default()
default_intents.members = True
bot = commands.Bot(command_prefix=get_pre, intents=default_intents)
bot.remove_command('help')

load_dotenv()


@bot.event
async def on_ready():
  await on_ready_event(bot)


@bot.event
async def on_command_error(ctx, error):
  await on_command_error_event(ctx, error, bot)


@bot.event
async def on_member_join(member):
  await on_member_join_event(member, bot)


@bot.event
async def on_member_remove(member):
  await on_member_remove_event(member, bot)


@bot.event
async def on_guild_join(guild):
  await on_guild_join_event(guild)


@bot.event
async def on_message(message):
  await on_message_event(message, bot)



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
