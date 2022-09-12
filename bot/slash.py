import discord
import aiosqlite3
import os
import random
import sys

sys.path.append("./files/slash")
sys.path.append("./files/ressources")


from connection import *
from bot import *

from poke import poke, rolls
from fun import stand
from utilities import servericon, usericon
from image_editing import level

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "ban", description = "Bans someone.")
    async def banCommand(self, ctx):
        await ban(ctx)

    @app_commands.command(name = "welcome", description = "Sets up welcome channel!")
    async def welcomeCommand(self, ctx):
        await welcome(ctx)

    @app_commands.command(name = "announcements", description = "Sets up Kanna's announcements channel!")
    async def announcementsCommand(self, ctx):
        await announcements(ctx)

    @app_commands.command(name = "clear", description = "Deletes recent messages.")
    async def clearCommand(self, ctx):
        await clear(ctx)

    @app_commands.command(name = "prune", description = "Deletes all (recent) messages from someone.")
    async def pruneCommand(self, ctx):
        await prune(ctx)

    @app_commands.command(name = "kick", description = "Kicks someone")
    async def kickCommand(self, ctx):
        await kick(ctx)

    @app_commands.command(name = "dice", description = "Rolls a dice!")
    async def diceCommand(self, ctx):
        await dice(ctx)

    @app_commands.command(name = "servericon", description = "Sends the server's icon.")
    async def servericonCommand(self, ctx):
        await servericon(ctx)

    @app_commands.command(name = "usericon", description = "Sends a user's icon.")
    @app_commands.describe(user="The user you want to see the icon of.")
    async def usericonCommand(self, interaction: discord.Interaction, user: discord.Member = None):
        if user == None:
        	user = ctx.author
        await usericon(ctx, user)

    @app_commands.command(name = "help", description = "Shows all commands.")
    async def helpCommand(self, ctx):
        await help(ctx)

    @app_commands.command(name = "level", description = "Shows your level!")
    @app_commands.describe(user="The user you would like to see the level of.")
    async def levelCommand(self, interaction: discord.Interaction, user: discord.Member = None):
        print(user)
        if user != None:
        	await level(interaction, user)
        else:
        	await level(interaction, interaction.author)

    @app_commands.command(name = "hug", description = "Hug Someone!")
    async def hugCommand(self, ctx):
        await hug(ctx)

    @app_commands.command(name = "stand", description = "Shows your assigned stand")
    async def standCommand(self, ctx):
        await stand(ctx)

    @app_commands.command(name = "poke", description = "Catches a pokémon!")
    async def pokeCommand(self, ctx):
        await poke(bot, ctx)

    @app_commands.command(name = "pokeinfo", description = "Shows a pokémon's infos!")
    async def pokeinfoCommand(self, ctx):
        await pokeinfo(bot, ctx)

    @app_commands.command(name = "rolls", description = "Shows the number of rolls you have.")
    async def rollsCommand(self, ctx):
        await rolls(ctx)

    @app_commands.command(name = "pokedex", description = "Shows your pokédex.")
    async def pokedexCommand(self, ctx):
        await pokedex(bot, ctx)

    @app_commands.command(name = "pokerank", description = "Shows the top 10 best PokéCatchers!")
    async def pokerankCommand(self, ctx):
        await pokerank(bot, ctx)
