from src.functions.funFunctions import *
from src.resources.bot import *
from src.resources.connection import *
from src.resources.mentions import *
from src.resources.prefix import *


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hug")
    async def hug(self, context):
        await hugFunction(ContextAdapter(context), get_target(context))

    @app_commands.command(name="hug", description="Lets you hug someone!")
    @app_commands.describe(user="The user you want to hug!")
    async def slashHug(
        self,
        interaction: discord.Interaction,
        user: Union[discord.Member, discord.User],
    ):
        await hugFunction(ContextAdapter(interaction), user)

    @commands.command(name="stand")
    async def stand(self, context):
        await standFunction(ContextAdapter(context))

    @app_commands.command(
        name="stand",
        description="Displays your assigned JJBA stand, your stand is bounded to you and won't change.",
    )
    async def slashStand(self, interaction: discord.Interaction):
        await standFunction(ContextAdapter(interaction))


async def setup(bot):
    await bot.add_cog(FunCog(bot))
