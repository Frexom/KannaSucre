import discord
from discord import app_commands
from discord.ext import commands

from src.functions.adminFunctions import (
    addlevelFunction,
    announceFunction,
    banFunction,
    editlevelsFunction,
    giveawayFunction,
    languageFunction,
    prefixFunction,
    togglelevelsFunction,
    welcomeFunction,
)
from src.resources.adapter import ContextAdapter


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix")
    async def prefix(self, context):
        prefix = context.message.content.split(" ")

        if len(prefix) > 1:
            await prefixFunction(ContextAdapter(context), prefix[1])
        else:
            await context.send("```" + context.prefix + "prefix *new prefix*```")

    @app_commands.command(
        name="prefix", description="Changes the bot prefix for this server only."
    )
    @app_commands.describe(prefix="The server's new prefix!")
    async def slashPrefix(self, interaction: discord.Interaction, prefix: str):
        await prefixFunction(ContextAdapter(interaction), prefix)

    @commands.command(name="ban")
    async def ban(self, context):
        words = context.message.content.split(" ")
        hasMention = len(context.message.mentions) > 0
        if hasMention:
            member = context.message.mentions[0]
            reason = " ".join(words[2:])
            await banFunction(ContextAdapter(context), member, reason)
        else:
            await context.send(
                "```" + context.prefix + "ban *mention target* *reason(optional)*```"
            )

    @app_commands.command(
        name="ban", description="Bans a specified user, a reason can be given or not."
    )
    @app_commands.describe(user="The user to ban.", reason="The reason to ban the user.")
    async def slashBan(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User,
        reason: str = None,
    ):
        await banFunction(ContextAdapter(interaction), user, reason)

    @commands.command(name="welcome")
    async def welcome(self, context):
        message = context.message
        if len(message.channel_mentions) > 0:
            channel = message.channel_mentions[0]

            if len(message.role_mentions) > 0:
                role = message.role_mentions[0]
                await welcomeFunction(ContextAdapter(context), channel, role)
            else:
                await welcomeFunction(ContextAdapter(context), channel)
        else:
            await context.send(
                "```" + context.prefix + "welcome *mention channel* *mention role(optional)*```"
            )

    @app_commands.command(
        name="welcome",
        description="Defines the jion and leaves log channel, and the role to give to new members.",
    )
    @app_commands.describe(channel="The channel you want the message to be sent.")
    @app_commands.describe(role="The role you want to give to new members.")
    async def slashWelcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        role: discord.Role = None,
    ):
        await welcomeFunction(ContextAdapter(interaction), channel, role)

    @commands.command(name="language")
    async def language(self, context):
        words = context.message.content.split(" ")
        locales = ["en", "fr"]  # tr soon
        if len(words) >= 2 and words[1] in locales:
            language = words[1]
            await languageFunction(ContextAdapter(context), language)
        else:
            await context.send("```" + context.prefix + "language en/fr```")

    @app_commands.command(
        name="language", description="Defines the language the bot uses on this server!"
    )
    @app_commands.choices(
        language=[
            app_commands.Choice(name="English", value="en"),
            app_commands.Choice(name="French", value="fr"),
        ]
    )
    @app_commands.describe(language="The language you want KannaSucre to use.")
    async def slashLanguage(
        self, interaction: discord.Interaction, language: discord.app_commands.Choice[str]
    ):
        await languageFunction(ContextAdapter(interaction), language.value)

    @commands.command(name="announce")
    async def announce(self, context):
        message = context.message.content.split(" ")
        channel = context.message.channel_mentions
        if len(channel) >= 1 and len(message) >= 3:
            announcement = " ".join(message[2:])
            await announceFunction(ContextAdapter(context), channel[0], announcement)
        else:
            await context.send("```" + context.prefix + "announce *mention channel* *message*```")

    @app_commands.command(
        name="announce", description="Sends a custom announcement on a set channel."
    )
    @app_commands.describe(message="The announcement message.")
    @app_commands.describe(channel="The channel to send the message")
    async def slashAnnounce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
    ):
        await announceFunction(ContextAdapter(interaction), channel, message)

    @commands.command(name="togglelevels")
    async def togglelevels(self, context):
        message = context.message.content.split(" ")
        toggle = message[1]
        if toggle.isnumeric() and (toggle == "0" or toggle == "1"):
            await togglelevelsFunction(ContextAdapter(context), int(toggle))
        else:
            await context.send("```" + context.prefix + "togglelevels 0 or 1```")

    @app_commands.command(name="togglelevels", description="Enable or disable the level feature.")
    @app_commands.choices(
        toggle=[
            app_commands.Choice(name="Disable", value=0),
            app_commands.Choice(name="Enable", value=1),
        ]
    )
    @app_commands.describe(toggle="Weather activating the level feature or not.")
    async def slashTogglelevels(self, interaction: discord.Interaction, toggle: int):
        await togglelevelsFunction(ContextAdapter(interaction), toggle)

    @commands.command(name="giveaway")
    async def giveaway(self, context):
        if not context.author.bot:
            content = bot.translator.getLocalString(ContextAdapter(context), "giveawayPrefix", [])
            await context.send(content=content)

    @app_commands.command(name="giveaway", description="Creates a new giveaway!")
    @app_commands.describe(channel="The channel to send the giveaway message.")
    @app_commands.describe(prize="The prize to win.")
    @app_commands.describe(days="The number of days the giveaway will last.")
    @app_commands.describe(hours="The number of hours the giveaway will last.")
    @app_commands.describe(minutes="The number of minutes the giveaway will last.")
    @app_commands.describe(role="The required role to enter the giveaway.")
    async def slashGiveaway(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        prize: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        role: discord.Role = None,
    ):
        await giveawayFunction(
            ContextAdapter(interaction), channel, prize, days, hours, minutes, role
        )

    @commands.command(name="editlevels")
    async def editlevels(self, context):
        await editlevelsFunction(ContextAdapter(context))

    @app_commands.command(name="editlevels", description="Edits the server's level rewards!")
    async def slashEditlevels(self, interaction):
        await editlevelsFunction(ContextAdapter(interaction))

    @commands.command(name="addlevel")
    async def addlevel(self, context: discord.Interaction):
        if not context.author.bot:
            message = context.message.content.split(" ")
            if (
                message[1].isdecimal()
                and int(message[1]) > 0
                and len(context.message.role_mentions) > 0
            ):
                level = int(message[1])
                role = context.message.role_mentions[0]

                await addlevelFunction(ContextAdapter(context), level, role)
            else:
                await context.send("```" + context.prefix + "addlevel *number* *role*```")

    @app_commands.command(name="addlevel", description="Adds a level reward!")
    @app_commands.describe(level="The level to reach to get the role.")
    @app_commands.describe(level="The rewarded role.")
    async def slashAddLevel(
        self, interaction: discord.Interaction, level: int, role: discord.Role
    ):
        await addlevelFunction(ContextAdapter(interaction), level, role)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
