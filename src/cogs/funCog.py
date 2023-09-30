import discord
from discord import app_commands
from discord.ext import commands

from src.functions.funFunctions import hugFunction, standFunction
from src.resources.adapter import ContextAdapter
from src.resources.mentions import get_target


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hug")
    async def hug(self, context):
        await hugFunction(self.bot, ContextAdapter(context), get_target(context))

    @app_commands.command(name="hug", description="Lets you hug someone!")
    @app_commands.describe(user="The user you want to hug!")
    async def slashHug(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User,
    ):
        await hugFunction(self.bot, ContextAdapter(interaction), user)

    @commands.command(name="stand")
    async def stand(self, context):
        await standFunction(self.bot, ContextAdapter(context))

    @app_commands.command(
        name="stand",
        description="Displays your assigned JJBA stand, your stand is bounded to you and won't change.",
    )
    async def slashStand(self, interaction: discord.Interaction):
        await standFunction(self.bot, ContextAdapter(interaction))


async def setup(bot):
    await bot.add_cog(FunCog(bot))
