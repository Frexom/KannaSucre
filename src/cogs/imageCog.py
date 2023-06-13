import discord
from discord import app_commands
from discord.ext import commands

from src.functions.imageFunctions import levelFunction
from src.resources.adapter import ContextAdapter
from src.resources.mentions import get_target


class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="level")
    async def level(self, context):
        user = get_target(context)

        await levelFunction(self.bot, ContextAdapter(context), user)

    @app_commands.command(name="level", description="Displays your level and XP.")
    @app_commands.describe(user="The user you want to see the level of.")
    async def slashLevel(self, interaction: discord.Interaction, user: discord.User = None):
        await levelFunction(self.bot, ContextAdapter(interaction), user)


async def setup(bot):
    await bot.add_cog(ImageCog(bot))
