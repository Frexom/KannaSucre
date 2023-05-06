from src.functions.utilitiesFunctions import *
from src.resources.bot import *
from src.resources.mentions import *
from src.resources.perms import *
from src.resources.prefix import *


class UtilitiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dice")
    async def dice(self, context):
        if not context.author.bot:
            words = context.message.content.split(" ")
            if len(words) > 1 and words[1].isdecimal() and int(words[1]) > 0:
                max = int(words[1])
                await diceFunction(ContextAdapter(context), max)
            else:
                await context.send("```" + context.prefix + "dice *number>0*```")

    @app_commands.command(name="dice", description="Rolls a dice!")
    @app_commands.describe(max="The largest number included.")
    async def slashDice(self, interaction: discord.Interaction, max: int = 6):
        await diceFunction(ContextAdapter(interaction), max)

    @commands.command(name="servericon")
    async def servericon(self, context):
        await servericonFunction(ContextAdapter(context))

    @app_commands.command(name="servericon", description="Shows the server's icon!")
    async def slashServericon(self, interaction: discord.Interaction):
        await servericonFunction(ContextAdapter(interaction))

    @commands.command(name="usericon")
    async def usericon(self, context):
        user = get_target(context)
        await usericonFunction(ContextAdapter(context), user)

    @app_commands.command(name="usericon", description="Shows an user's avatar!")
    @app_commands.describe(member="The user you want to see the avatar of!")
    async def slashUsericon(
        self,
        interaction: discord.Interaction,
        member: Union[discord.Member, discord.User] = None,
    ):
        await usericonFunction(ContextAdapter(interaction), member)

    @commands.command(name="supportserver")
    async def supportserver(self, context):
        await supportserverFunction(ContextAdapter(context))

    @app_commands.command(
        name="supportserver",
        description="Get an invite to KannaSucre's support server!",
    )
    async def slashSupportserver(self, interaction: discord.Interaction):
        await supportserverFunction(ContextAdapter(interaction))

    @commands.command(name="daily")
    async def daily(self, context):
        await dailyFunction(ContextAdapter(context))

    @app_commands.command(name="daily", description="Get your daily KannaSucre money!")
    async def slashDaily(self, interaction: discord.Interaction):
        await dailyFunction(ContextAdapter(interaction))

    @commands.command(name="servrank")
    async def servrank(self, context):
        await servrankFunction(ContextAdapter(context))

    @app_commands.command(
        name="servrank", description="See this server's most active members!"
    )
    async def slashServrank(self, interaction: discord.Interaction):
        await servrankFunction(ContextAdapter(interaction))

    @commands.command(name="help")
    async def help(self, context):
        message_list = context.message.content.split(" ")
        if len(message_list) < 2:
            await helpFunction(ContextAdapter(context))
        else:
            command = message_list[1]
            await helpFunction(ContextAdapter(context), command)

    @app_commands.command(name="help", description="Get some help about the commands!")
    @app_commands.describe(command="Name of the command you want the details of!")
    async def slashHelp(self, interaction=discord.Interaction, command: str = None):
        await helpFunction(ContextAdapter(interaction), command)


async def setup(bot):
    await bot.add_cog(UtilitiesCog(bot))
