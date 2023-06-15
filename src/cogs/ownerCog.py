import os

import discord
from discord import app_commands
from discord.ext import commands

from src.functions.ownerFunctions import (
    databaseFunction,
    guildcountFunction,
    previewFunction,
    reloadFunction,
    shutdownFunction,
    sqlFunction,
    statusFunction,
    syncFunction,
)
from src.resources.adapter import ContextAdapter
from src.resources.prefix import get_pre


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="preview")
    @commands.is_owner()
    async def preview(self, context):
        message = context.message.content.split(" ")[1:]
        message = " ".join(message)
        await previewFunction(self.bot, ContextAdapter(context), message)

    @app_commands.command(name="preview", description="Makes the bot repeat what you just said.")
    @app_commands.describe(message="The message to repeat.")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashPreview(self, interaction: discord.Interaction, message: str):
        await previewFunction(self.bot, ContextAdapter(interaction), message)

    @commands.command(name="sql")
    @commands.is_owner()
    async def sql(self, context):
        query = context.message.content.split(" ")[1:]
        query = " ".join(query)
        await sqlFunction(self.bot, ContextAdapter(context), query)

    @app_commands.command(name="sql", description="Runs SQL queries, be careful!")
    @app_commands.describe(query="The query to run.")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashSql(self, interaction: discord.Interaction, query: str):
        await sqlFunction(self.bot, ContextAdapter(interaction), query)

    @commands.command(name="database")
    @commands.is_owner()
    async def database(self, context):
        await databaseFunction(self.bot, ContextAdapter(context))

    @app_commands.command(
        name="database",
        description="Sends the bot's database to the current channel, BE CAREFUL.",
    )
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashDatabase(self, interaction: discord.Interaction):
        await databaseFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, context):
        await shutdownFunction(self.bot, ContextAdapter(context))

    @app_commands.command(name="shutdown", description="Shuts down the bot, BE CAREFUL.")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashShutdown(self, interaction: discord.Interaction):
        await shutdownFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="sync")
    @commands.is_owner()
    async def syncCommands(self, context: discord.ext.commands.Context):
        await syncFunction(self.bot, ContextAdapter(context))

    @app_commands.command(name="sync", description="Sync the bot's commands.")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashSync(self, interaction: discord.Interaction):
        await syncFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="rules")
    @commands.is_owner()
    # This command does not have a slash version,
    # and is only used to dislpay rules on the bot's community server
    async def rules(self, context):
        e = discord.Embed(
            title=context.guild.name + " rules",
            description="Please note that any violation of those rules will be likely to result in a ban, if justified.\n\n\n",
        )
        e.add_field(
            name="Rule :one: : Respect",
            inline=False,
            value="Respect eachother, everyone here is considered equal, regardless of their gender, sexuality and origin. Do not discrimiate, discomfort or insult anyone here.\n\n\n",
        )
        e.add_field(
            name="Rule :two: : NSFW/Spam",
            inline=False,
            value="NSFW and spam are here strictly prohibed, this server must be able to welcome people regardless of their age.\n\n\n",
        )
        e.add_field(
            name="Rule :three: : Channels",
            inline=False,
            value="Respect the use of each channel, you can read a channel's description to see what is allowed and what isn't.",
        )
        e.add_field(
            name="Rule :four: : Profile",
            inline=False,
            value="No offensive profile picture or name. No one should be seeing offensive or sensitive content while clicking your profile.",
        )
        e.set_thumbnail(url=context.guild.icon.url)
        await context.channel.send(embed=e)

    @commands.command(name="guildcount")
    @commands.is_owner()
    async def guildcount(self, context):
        await guildcountFunction(self.bot, ContextAdapter(context))

    @app_commands.command(name="guildcount", description="Shows how many guilds the bot is in.")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashGuildcount(self, interaction: discord.Interaction):
        await guildcountFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="status")
    @commands.is_owner()
    async def status(self, context):
        msg = context.message.content.split(" ")
        validStatuses = ["online", "dnd", "idle"]
        isLongEnough = len(msg) > 2

        if isLongEnough and msg[1].lower() in validStatuses:
            activity = discord.Game(" ".join(msg[2:]))
            await statusFunction(self.bot, ContextAdapter(context), msg[1].lower(), activity)
        else:
            await context.send(
                content=f"```{await get_pre(context)}status online/dnd/idle *activity*```"
            )

    @app_commands.command(name="status", description="Changes the status of the bot!")
    @app_commands.describe(activity="The new activity!")
    @app_commands.describe(status="The new status!")
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Online", value="online"),
            app_commands.Choice(name="DoNotDisturb", value="dnd"),
            app_commands.Choice(name="Idle", value="idle"),
        ]
    )
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashStatus(
        self,
        interaction: discord.Interaction,
        status: app_commands.Choice[str] = "online",
        activity: str = "Now with Slash commands!",
    ):
        await statusFunction(self.bot, ContextAdapter(interaction), status, activity)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, context):
        await reloadFunction(self.bot, ContextAdapter(context))

    @app_commands.command(name="reload", description="Reloads the bot's cogs!")
    @app_commands.guilds(int(os.environ["TESTGUILDID"]))
    async def slashReload(self, interaction: discord.Interaction):
        await reloadFunction(self.bot, ContextAdapter(interaction))


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
