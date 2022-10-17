from datetime import datetime, timedelta

from mentions import *
from prefix import *
from perms import *
from bot import *


sys.path.append("../ressources")

class slashModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name = "prune", description = "Deletes all the defined user's messages among the 200 lastest from each channel.")
    @app_commands.describe(user="The user to prune.")
    async def prune(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.manage_messages:
                if not user.guild_permissions.manage_messages:
                    await interaction.response.defer()

                    def checkUser(m):
                        return m.author == user

                    mess_count = 0
                    for channel in interaction.guild.text_channels:
                        try:
                            mess_count += len(await channel.purge(limit = 200, check = checkUser, reason = "Pruning " + user.name + "'s messages.'"))
                        except Exception:
                            pass


                    content = await getLocalString(interaction.guild.id, "strings", "pruneUser", [("number", str(mess_count)), ("user", user.name), ("guild", interaction.guild.name)])
                    await interaction.followup.send(content = content, ephemeral=True)
                else:
                    await lack_perms(interaction, "prune")
            else:
                await missing_perms(interaction, "prune", "manage messages")


    @app_commands.command(name="clear", description = "Clear a given number of messages (maximum 50).")
    @app_commands.describe(amount = "The amount of messages to delete.")
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.manage_messages:
                if amount < 50:
                    await interaction.response.defer()
                    try:
                        mess_count = len(await interaction.channel.purge(limit = amount, before=datetime.now()-timedelta(seconds=1), reason = "Requested by " + interaction.user.name))
                    except Exception:
                        content =  await getLocalString(interaction.guild.id, "strings", "noAccess", [])
                        await interaction.followup.send(content = content)
                        return

                    content = await getLocalString(interaction.guild.id, "strings", "clearMessages", [("number", mess_count)])
                    await interaction.followup.send(content = content, ephemeral=True)
                else:
                    content = await getLocalString(interaction.guild.id, "strings", "clearMore", [])
                    await interaction.response.send_message(content = content)
            else:
                await missing_perms(interaction, "clear", "manage messages")


    @app_commands.command(name="kick", description = "Kicks a specified user, a reason can be given or not.")
    @app_commands.describe(user="The user to kick.", reason = "The reason to kick the user.")
    async def kick(self, interaction:discord.Interaction, user: discord.Member, reason: str = None):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.kick_members:
                if not user.guild_permissions.kick_members:
                    if reason is None:
                        content = await getLocalString(interaction.guild.id, "strings", "kickNoReason", [("guild", interaction.guild.name)])
                        await user.send(content = content)
                    else:
                        content = await getLocalString(interaction.guild.id, "strings", "kickReason", [("guild", interaction.guild.name), ("reason", reason)])
                        await user.send(content = content)
                    await user.kick(reason = (reason or "No reason given.") + " / Triggered by " + interaction.user.name)
                    content = await getLocalString(interaction.guild.id, "strings", "userKicked", [])
                    await interaction.response.send_message(content = content)
                else:
                     await lack_perms(interaction, "kick")
            else:
                await missing_perms(interaction, "kick", "kick members")
