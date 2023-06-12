import discord
from discord import app_commands
from discord.ext import commands

from src.functions.moderationFunctions import clearFunction, kickFunction, pruneFunction
from src.resources.adapter import ContextAdapter
from src.resources.mentions import get_mention


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prune")
    async def prune(self, context):
        user = get_mention(context)
        if user is not None:
            await pruneFunction(ContextAdapter(context), user)
        else:
            await context.send("```" + context.prefix + "prune *mention targeted user*```")

    @app_commands.command(
        name="prune",
        description="Deletes all the defined user's messages among the 200 lastest from each channel.",
    )
    @app_commands.describe(user="The user to prune.")
    async def slashPrune(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User,
    ):
        await pruneFunction(ContextAdapter(interaction), user)

    @commands.command(name="clear")
    async def clear(self, context):
        words = context.message.content.split(" ")
        if len(words) > 1 and words[1].isdecimal():
            await clearFunction(ContextAdapter(context), int(words[1]))
        else:
            await context.send("```" + context.prefix + "clear *number of messages*```")

    @app_commands.command(
        name="clear", description="Clear a given number of messages (maximum 50)."
    )
    @app_commands.describe(amount="The amount of messages to delete.")
    async def slashClear(self, interaction: discord.Interaction, amount: int):
        await clearFunction(ContextAdapter(interaction), amount)

    @commands.command(name="kick")
    async def kick(self, context):
        words = context.message.content.split(" ")
        hasMention = len(context.message.mentions) > 0
        if hasMention:
            member = context.message.mentions[0]
            reason = " ".join(words[2:])
            await kickFunction(ContextAdapter(context), member, reason)
        else:
            await context.send(
                "```" + context.prefix + "ban *mention target* *reason(optional)*```"
            )

    @app_commands.command(
        name="kick", description="Kicks a specified user, a reason can be given or not."
    )
    @app_commands.describe(user="The user to kick.", reason="The reason to kick the user.")
    async def slashKick(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User,
        reason: str = None,
    ):
        await kickFunction(ContextAdapter(interaction), user, reason)


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
