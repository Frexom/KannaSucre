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
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.manage_guild:
                    if ' ' not in prefix:
                        connection, cursor = await get_conn("./files/ressources/bot.db")
                        await cursor.execute("UPDATE dis_guild SET guild_prefix = ? WHERE guild_id = ?", (prefix, interaction.guild.id))
                        content = bot.translator.getLocalString(interaction, "newPrefix", [("prefix", str(prefix))])
                        await interaction.response.send_message(content = content)
                        await connection.commit()
                        await close_conn(connection, cursor)
                    else:
                        content = bot.translator.getLocalString(interaction, "prefixNoSpace", [])
                        await interaction.response.send_message(content = content)
                else:
                    await missing_perms(interaction, "prefix", "manage guild")
            else:
                await dmUnavailable(interaction, "prefix")

    @app_commands.command(name = "ban", description ="Bans a specified user, a reason can be given or not.")
    @app_commands.describe(user = "The user to ban.", reason="The reason to ban the user.")
    async def ban(self, interaction: discord.Interaction, user: Union[discord.Member, discord.User], reason : str = None):
        if not interaction.user.bot :
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.ban_members:
                    if not user.guild_permissions.ban_members:

                        if reason is not None:
                            content = bot.translator.getLocalString(interaction, "banReason", [("guild", interaction.guild.name), ("reason", reason)])
                            await user.send(content = content)
                        else:
                            content = bot.translator.getLocalString(interaction, "banNoReason", [("guild", interaction.guild.name)])
                            await user.send(content = content)
                        await user.ban(reason = (reason or "No reason given.") + " / Triggered by " + interaction.user.name)
                        content = bot.translator.getLocalString(interaction, "userBanned", [])
                        await interaction.response.send_message(content = content)
                    else:
                        await lack_perms(interaction, "ban")
                else:
                    await missing_perms(interaction, "ban", "ban members")
            else:
                await dmUnavailable(interaction, "ban")


    @app_commands.command(name="welcome", description = "Defines the jion and leaves log channel, and the role to give to new members.")
    @app_commands.describe(channel="The channel you want the message to be sent.")
    @app_commands.describe(role="The role you want to give to new members.")
    async def welcome(self, interaction: discord.Interaction, channel : discord.TextChannel = None, role : discord.Role = None):
        if not interaction.user.bot :
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.manage_guild:

                    connection, cursor = await get_conn("./files/ressources/bot.db")
                    content = ""

                    if channel is None:
                        channel = 0
                        content += bot.translator.getLocalString(interaction, "welcomeDisabled", [])
                        await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (0, 0, interaction.guild.id))
                    else:
                        channel = channel.id
                        content += bot.translator.getLocalString(interaction, "welcomeChannel", [("channel", channel)])

                        content += "\n"

                        if role is not None and role.name != "@everyone":
                            content += bot.translator.getLocalString(interaction, "welcomeRole", [("role", role.name)])
                            await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (channel, role.id, interaction.guild.id))
                        else:
                            content += bot.translator.getLocalString(interaction, "welcomeNoRole", [])
                            await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (channel, 0, interaction.guild.id))

                    await interaction.response.send_message(content = content)

                    await connection.commit()
                    await close_conn(connection, cursor)
                else:
                    await missing_perms(interaction, "welcome", "manage guild")
            else:
                await dmUnavailable(interaction, "welcome")


    @app_commands.command(name="language", description="Defines the language the bot uses on this server!")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="en")
        ,app_commands.Choice(name="French", value="fr")
#        ,app_commands.Choice(name="French", value="es")
    ])
    @app_commands.describe(language="The language you want KannaSucre to use.")
    async def language(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        if not interaction.user.bot:
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.manage_guild:
                    connection, cursor = await get_conn("./files/ressources/bot.db")
                    await cursor.execute("UPDATE dis_guild SET guild_locale = ? WHERE guild_id = ?", (language.value, interaction.guild.id))
                    await connection.commit()
                    bot.translator.updateCache(interaction.guild.id, language.value)

                    content = bot.translator.getLocalString(interaction, "newLanguage", [])
                    await interaction.response.send_message(content = content)
                else:
                    await missing_perms(interaction, "language", "manage guild")
            else:
                await dmUnavailable(interaction, "language")


    @app_commands.command(name = "announce", description = "Sends a custom announcement on a set channel.")
    @app_commands.describe(message="The announcement message.")
    @app_commands.describe(channel="The channel to send the message")
    async def announce(self, interaction : discord.Interaction, channel : discord.TextChannel, message: str):
        if not interaction.user.bot:
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.manage_guild:
                    if interaction.user.id == int(os.environ['OWNER_ID']):
                        authorCredit = ""
                    else:
                        authorCredit = bot.translator.getLocalString(interaction, "announceAuthor", [("user", interaction.user.mention)])

                    if(channel.guild.id == interaction.guild.id):
                        message = await channel.send(authorCredit+message)
                        content = bot.translator.getLocalString(interaction, "announceLink", [])
                        await interaction.response.send_message(content + message.jump_url)
                    else:
                        content = bot.translator.getLocalString(interaction, "channelGuild", [])
                        await interaction.response.send_message(content = content)
                else:
                    await missing_perms(interaction, "announce", "manage guild")
            else:
                await dmUnavailable(interaction, "announce")


    @app_commands.command(name = "togglelevels", description = "Enable or disable the level feature.")
    @app_commands.choices(toggle=[
        app_commands.Choice(name="Disable", value=0)
        ,app_commands.Choice(name="Enable", value=1)
    ])
    @app_commands.describe(toggle="Weather activating the level feature or not.")
    async def toggleLevels(self, interaction: discord.Interaction, toggle:int):
        if not interaction.user.bot:
            if(interaction.guild is not None):
                if interaction.user.guild_permissions.manage_guild:
                    connection, cursor = await get_conn("./files/ressources/bot.db")
                    await cursor.execute("UPDATE dis_guild SET guild_levels_enabled = ? WHERE guild_id = ?", (toggle, interaction.guild.id))
                    await connection.commit()

                    if toggle == 1:
                        content = bot.translator.getLocalString(interaction, "togglelevelsEnabled", [])
                        await interaction.response.send_message(content = content)
                    else:
                        content = bot.translator.getLocalString(interaction, "togglelevelsDisabled", [])
                        await interaction.response.send_message(content = content)
                else:
                    await missing_perms(interaction, "togglelevels", "manage guild")
            else:
                await dmUnavailable(interaction, "togglelevels")

    @app_commands.command(name = "giveaway", description = "Creates a new giveaway!")
    @app_commands.describe(channel="The channel to send the giveaway message.")
    @app_commands.describe(prize="The prize to win.")
    @app_commands.describe(days="The number of days the giveaway will last.")
    @app_commands.describe(hours="The number of hours the giveaway will last.")
    @app_commands.describe(minutes="The number of minutes the giveaway will last.")
    @app_commands.describe(role="The required role to enter the giveaway.")
    async def slashGiveaway(self, interaction: discord.Interaction, channel: discord.TextChannel, prize: str, days: int = 0, hours: int = 0, minutes: int = 0, role: discord.Role = None):
        if not interaction.user.bot:
            if(interaction.guild is not None):
                if(interaction.user.guild_permissions.manage_guild):
                    #Convert to seconds
                    duration = days*24*60*60 + hours*60*60 + minutes*60
                    if(duration != 0):

                        #Check if channel on guild
                        channelOnGuild = False
                        for checkChannel in interaction.guild.text_channels:
                            if(checkChannel.id == channel.id):
                                channelOnGuild = True

                        #If channel is found
                        if(channelOnGuild):
                            embed = GiveawayEmbed(interaction, duration, prize, role)


                            #Try sending the giveaway
                            try:
                                givMess = await channel.send(embed = embed, view = giveawayView())
                            #If channel not reachable
                            except discord.errors.Forbidden:
                                content = "I don't have the permission to send messages in this channel :/"
                                await interaction.response.send_message(content = content)

                            content = "The giveaway was created!"
                            await interaction.response.send_message(content = content)

                            connection, cursor = await get_conn("./files/ressources/bot.db")
                            if(role != None and role.name != "@everyone"):
                                await cursor.execute("INSERT INTO giv_giveaway(giv_message_id, giv_prize, giv_channel_id, giv_end_date, giv_role_id) VALUES (?,?,?,?,?)", (givMess.id, prize, channel.id, time.time()+duration, role.id))
                            else:
                                await cursor.execute("INSERT INTO giv_giveaway(giv_message_id, giv_prize, giv_channel_id, giv_end_date, giv_role_id) VALUES (?,?,?,?,?)", (givMess.id, prize, channel.id, time.time()+duration, 0))
                            await connection.commit()
                            await close_conn(connection, cursor)

                        else:
                            content = bot.translator.getLocalString(interaction, "channelGuild", [])
                            await interaction.response.send_message(content = content)
                    else:
                        content = "Please input a duration."
                        await interaction.response.send_message(content=content)
                else:
                    await missing_perms(interaction, "giveaway", "manage guild")
            else:
                await dmUnavailable(interaction, "giveaway")
