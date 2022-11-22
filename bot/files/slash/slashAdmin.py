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
                t = Translator(interaction.guild.id, loadStrings=True)
                content = t.getLocalString("newPrefix", [("prefix", str(prefix))])
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

                    t = Translator(interaction.guild.id, loadStrings = True)

                    if reason is not None:
                        content = t.getLocalString("banReason", [("guild", interaction.guild.name), ("reason", reason)])
                        await user.send(content = content)
                    else:
                        content = t.getLocalString("banNoReason", [("guild", interaction.guild.name)])
                        await user.send(content = content)
                    await user.ban(reason = (reason or "No reason given.") + " / Triggered by " + interaction.user.name)
                    content = t.getLocalString("userBanned", [])
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

                t = Translator(interaction.guild.id, loadStrings=True)

                if channel is None:
                    channel = 0
                    content = t.getLocalString("welcomeDisabled", [])
                    await interaction.response.send_message(content = content)
                else:
                    channel = channel.id
                    content = t.getLocalString("welcomeChannel", [("channel", channel)])
                    await interaction.response.send_message(content = content)

                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE guilds SET guild_welcome_channel_id = ? WHERE guild_id=?", (channel, interaction.guild.id))
                await connection.commit()
                await close_conn(connection, cursor)
            else:
                await missing_perms(interaction, "welcome", "manage guild")


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

                t = Translator(interaction.guild.id, loadStrings = True)
                content = t.getLocalString("newLanguage", [])
                await interaction.response.send_message(content = content)
            else:
                await missing_perms(interaction, "language", "manage guild")


    @app_commands.command(name = "announce", description = "Sends a custom announcement on a set channel.")
    @app_commands.describe(message="The announcement message.")
    @app_commands.describe(channel="The channel to send the message")
    async def announce(self, interaction : discord.Interaction, channel : discord.TextChannel, message: str):
        if not interaction.user.bot:
            if interaction.user.guild_permissions.manage_guild:
                if interaction.user.id == int(os.environ['OWNER_ID']) and False:
                    authorCredit = ""
                else:
                    authorCredit = "*Message sent by **" + interaction.user.name + "#" + interaction.user.discriminator + "** :*\n"

                if(channel.guild.id == interaction.guild.id):
                    message = await channel.send(authorCredit+message)
                    await interaction.response.send_message("Done!\n Click here to go to message : " + message.jump_url)
                else:
                    await interaction.response.send_message("This channel isn't on this guild!")
            else:
                await missing_perms(interaction, "announce", "manage guild")
