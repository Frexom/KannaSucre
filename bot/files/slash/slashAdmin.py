from connection import *
from prefix import *
from perms import *
from bot import *

sys.path.append("../ressources")

class slashAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "prefix", description = "Changes the bot prefix for this server only.")
    @app_commands.describe(prefix = "The server's new prefix!")
    async def prefix(self, interaction: discord.Interaction, prefix: str):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.manage_guild:
                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE guilds SET guild_prefix = ? WHERE guild_id = ?", (prefix, interaction.guild.id))
                content = await getLocalString(interaction.guild.id, "strings", "newPrefix", [("prefix", str(prefix))])
                await interaction.response.send_message(content = content)
                await connection.commit()
                await close_conn(connection, cursor)
            else:
                await missing_perms(interaction, "prefix", "manage guild")

    @app_commands.command(name = "ban", description ="Bans a specified user, a reason can be given or not.")
    @app_commands.describe(user = "The user to ban.", reason="The reason to ban the user.")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason : str = None):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.ban_members:
                if not user.guild_permissions.ban_members:
                    if reason is not None:
                        content = await getLocalString(interaction.guild.id, "strings", "banReason", [("guild", interaction.guild.name), ("reason", reason)])
                        await user.send(content = content)
                    else:
                        content = await getLocalString(interaction.guild.id, "strings", "banNoReason", [("guild", interaction.guild.name)])
                        await user.send(content = content)
                    await user.ban(reason = (reason or "No reason given.") + " / Triggered by " + interaction.user.name)
                    content = await getLocalString(interaction.guild.id, "strings", "userBanned", [])
                    await interaction.response.send_message(content = content)
                else:
                    await lack_perms(interaction, "ban")
            else:
                await missing_perms(interaction, "ban", "ban members")


    @app_commands.command(name="welcome", description = "Defines welcome channel where users arrivals and departures are announced.")
    @app_commands.describe(channel="The channel you want the message to be sent.")
    async def welcome(self, interaction: discord.Interaction, channel : discord.TextChannel = None):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.manage_guild:
                if channel is None:
                    channel = 0
                    content = await getLocalString(interaction.guild.id, "strings", "welcomeDisabled", [])
                    await interaction.response.send_message(content = content)
                else:
                    channel = channel.id
                    content = await getLocalString(interaction.guild.id, "strings", "welcomeChannel", [("channel", channel)])
                    await interaction.response.send_message(content = content)

                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE guilds SET guild_welcome_channel_id = ? WHERE guild_id=?", (channel, interaction.guild.id))
                await connection.commit()
                await close_conn(connection, cursor)
            else:
                await missing_perms(interaction, "welcome", "manage guild")


    @app_commands.command(name="announcements", description = "Defines announcements channel where KannaSucre's updates notices will be sent.")
    @app_commands.describe(channel="The channel you want the message to be sent.")
    async def announcements(self, interaction: discord.Interaction, channel : discord.TextChannel = None):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.manage_guild:
                if channel is None:
                    channel = 0
                    content = await getLocalString(interaction.guild.id, "strings", "announcementsDisabled", [])
                    await interaction.response.send_message(content = content)
                else:
                    channel = channel.id
                    content = await getLocalString(interaction.guild.id, "strings", "announcementsChannel", [("channel", channel)])
                    await interaction.response.send_message("Announcements messages will now be sent in <#" + str(channel) + ">.")

                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE guilds SET guild_announcements_channel_id = ? WHERE guild_id=?", (channel, interaction.guild.id))
                await connection.commit()
                await close_conn(connection, cursor)
            else:
                await missing_perms(interaction, "announcements", "manage guild")

    @app_commands.command(name="language", description="Defines the language the bot uses on this server!")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="en")
        ,app_commands.Choice(name="French", value="fr")
#        ,app_commands.Choice(name="French", value="es")
    ])
    @app_commands.describe(language="The language you want KannaSucre to use.")
    async def language(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        if not interaction.user.bot:
            if interaction.user.guild_permissions.manage_guild:
                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE guilds SET guild_locale = ? WHERE guild_id = ?", (language.value, interaction.guild.id))
                await connection.commit()
                content = await getLocalString(interaction.guild.id, "strings", "newLanguage", [])
                await interaction.response.send_message(content = content)
            else:
                await missing_perms(interaction, "language", "manage guild")
