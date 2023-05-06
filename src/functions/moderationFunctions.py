from src.resources.bot import *
from src.resources.mentions import *
from src.resources.perms import *
from src.resources.prefix import *


async def pruneFunction(
    interaction: ContextAdapter, user: Union[discord.Member, discord.User]
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_messages:
                if not user.guild_permissions.manage_messages:
                    await interaction.defer()

                    def checkUser(m):
                        return m.author == user

                    mess_count = 0
                    for channel in interaction.getGuild().text_channels:
                        try:
                            mess_count += len(
                                await channel.purge(
                                    limit=200,
                                    check=checkUser,
                                    reason="Pruning " + user.name + "'s messages.'",
                                )
                            )
                        except Exception:
                            pass

                    content = bot.translator.getLocalString(
                        interaction,
                        "pruneUser",
                        [
                            ("number", str(mess_count)),
                            ("user", user.name),
                            ("guild", interaction.getGuild().name),
                        ],
                    )
                    await interaction.followupSend(content=content, ephemeral=True)
                else:
                    await lack_perms(interaction, "prune")
            else:
                await missing_perms(interaction, "prune", "manage messages")
        else:
            await dmUnavailable(interaction, "prune")


async def clearFunction(interaction: ContextAdapter, amount: int):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_messages:
                if amount <= 50:

                    if interaction.isContext():
                        amount += 1
                    else:
                        content = bot.translator.getLocalString(
                            interaction, "clearDelete", []
                        )
                        await interaction.sendMessage(content=content, ephemeral=True)

                    try:
                        mess_count = len(
                            await interaction.getChannel().purge(
                                limit=amount,
                                reason="Requested by " + interaction.getAuthor().name,
                            )
                        )

                        if interaction.isContext():
                            mess_count += -1

                    except discord.errors.Forbidden:
                        content = bot.translator.getLocalString(
                            interaction, "noAccess", []
                        )
                        await interaction.followupSend(content=content)
                        return

                    content = bot.translator.getLocalString(
                        interaction, "clearMessages", [("number", mess_count)]
                    )
                    if interaction.isContext():
                        await interaction.followupSend(content=content, delete_after=5)
                    else:
                        await interaction.editOriginal(content=content)
                else:
                    content = bot.translator.getLocalString(
                        interaction, "clearMore", []
                    )
                    await interaction.sendMessage(content=content)
            else:
                await missing_perms(interaction, "clear", "manage messages")
        else:
            await dmUnavailable(interaction, "clear")


async def kickFunction(
    interaction: ContextAdapter,
    user: Union[discord.Member, discord.User],
    reason: str = None,
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.kick_members:
                if not user.guild_permissions.kick_members:

                    if reason == "" or reason is None:
                        content = bot.translator.getLocalString(
                            interaction,
                            "kickNoReason",
                            [("guild", interaction.getGuild().name)],
                        )
                        try:
                            await user.send(content=content)
                        except discord.errors.HTTPException:
                            pass
                    else:
                        content = bot.translator.getLocalString(
                            interaction,
                            "kickReason",
                            [
                                ("guild", interaction.getGuild().name),
                                ("reason", reason),
                            ],
                        )
                        try:
                            await user.send(content=content)
                        except discord.errors.HTTPException:
                            pass
                    await user.kick(
                        reason=(reason or "No reason given.")
                        + " / Triggered by "
                        + interaction.getAuthor().name
                    )
                    content = bot.translator.getLocalString(
                        interaction, "userKicked", []
                    )
                    await interaction.sendMessage(content=content)

                else:
                    await lack_perms(interaction, "kick")
            else:
                await missing_perms(interaction, "kick", "kick members")
        else:
            await dmUnavailable(interaction, "kick")
