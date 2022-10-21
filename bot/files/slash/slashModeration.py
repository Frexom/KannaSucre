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

                    t = Translator(interaction.guild.id, loadStrings = True)
                    content = t.getLocalString("pruneUser", [("number", str(mess_count)), ("user", user.name), ("guild", interaction.guild.name)])
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
                t = Translator(interaction.guild.id, loadStrings=True)
                if amount < 50:
                    await interaction.response.defer()

                    try:
                        mess_count = len(await interaction.channel.purge(limit = amount, before=datetime.now()-timedelta(seconds=1), reason = "Requested by " + interaction.user.name))
                    except Exception:
                        content =  t.getLocalString("noAccess", [])
                        await interaction.followup.send(content = content)
                        return

                    content = t.getLocalString("clearMessages", [("number", mess_count)])
                    await interaction.followup.send(content = content, ephemeral=True)
                else:
                    content = t.getLocalString("clearMore", [])
                    await interaction.response.send_message(content = content)
            else:
                await missing_perms(interaction, "clear", "manage messages")


    @app_commands.command(name="kick", description = "Kicks a specified user, a reason can be given or not.")
    @app_commands.describe(user="The user to kick.", reason = "The reason to kick the user.")
    async def kick(self, interaction:discord.Interaction, user: discord.Member, reason: str = None):
        if not interaction.user.bot :
            if interaction.user.guild_permissions.kick_members:
                if not user.guild_permissions.kick_members:

                    t = Translator(interaction.guild.id, loadStrings = True)
                    if reason is None:
                        content = t.getLocalString("kickNoReason", [("guild", interaction.guild.name)])
                        await user.send(content = content)
                    else:
                        content = t.getLocalString("kickReason", [("guild", interaction.guild.name), ("reason", reason)])
                        await user.send(content = content)
                    await user.kick(reason = (reason or "No reason given.") + " / Triggered by " + interaction.user.name)
                    content = t.getLocalString("userKicked", [])
                    await interaction.response.send_message(content = content)

                else:
                     await lack_perms(interaction, "kick")
            else:
                await missing_perms(interaction, "kick", "kick members")
