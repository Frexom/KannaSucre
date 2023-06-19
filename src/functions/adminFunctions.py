import os
import time

import discord
from discord import app_commands

from src.resources.adapter import ContextAdapter
from src.resources.perms import lack_perms, missing_perms
from src.resources.persistent import GiveawayEmbed, GiveawayView
from src.resources.prefix import Prefix
from src.resources.ui import LevelListEmbed, LevelListView


async def prefixFunction(bot, interaction: ContextAdapter, prefix: str):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                if " " not in prefix:
                    cursor = await bot.connection.cursor()
                    await cursor.execute(
                        "UPDATE dis_guild SET guild_prefix = ? WHERE guild_id = ?",
                        (prefix, interaction.getGuild().id),
                    )
                    Prefix.updateCache(interaction.getGuild().id, prefix)
                    content = bot.translator.getLocalString(
                        interaction, "newPrefix", [("prefix", str(prefix))]
                    )
                    await interaction.sendMessage(content=content)
                    await bot.connection.commit()
                    await cursor.close()
                else:
                    content = bot.translator.getLocalString(interaction, "prefixNoSpace", [])
                    await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "prefix", "manage guild")
        else:
            awFunctionmUnavailable(interaction, "prefix")


async def banFunction(
    bot,
    interaction: ContextAdapter,
    user: discord.Member | discord.User,
    reason: str = None,
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.ban_members:
                if not user.guild_permissions.ban_members:

                    if reason != "" and reason is not None:
                        content = bot.translator.getLocalString(
                            interaction,
                            "banReason",
                            [
                                ("guild", interaction.getGuild().name),
                                ("reason", reason),
                            ],
                        )
                        try:
                            await user.send(content=content)
                        except discord.errors.HTTPException:
                            pass
                    else:
                        content = bot.translator.getLocalString(
                            interaction,
                            "banNoReason",
                            [("guild", interaction.getGuild().name)],
                        )
                        try:
                            await user.send(content=content)
                        except discord.errors.HTTPException:
                            pass
                    await user.ban(
                        reason=(reason or "No reason given.")
                        + " / Triggered by "
                        + interaction.getAuthor().display_name
                    )
                    content = bot.translator.getLocalString(interaction, "userBanned", [])
                    await interaction.sendMessage(content=content)
                else:
                    await lack_perms(bot, interaction, "ban")
            else:
                await missing_perms(bot, interaction, "ban", "ban members")
        else:
            await dmUnavailable(interaction, "ban")


async def welcomeFunction(
    bot,
    interaction: ContextAdapter,
    channel: discord.TextChannel = None,
    role: discord.Role = None,
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:

                cursor = await bot.connection.cursor()
                content = ""

                if channel is None:
                    channel = 0
                    content += bot.translator.getLocalString(interaction, "welcomeDisabled", [])
                    await cursor.execute(
                        "UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?",
                        (0, 0, interaction.getGuild().id),
                    )
                else:
                    channel = channel.id
                    content += bot.translator.getLocalString(
                        interaction, "welcomeChannel", [("channel", channel)]
                    )

                    content += "\n"

                    if role is not None and role.name != "@everyone":
                        content += bot.translator.getLocalString(
                            interaction, "welcomeRole", [("role", role.name)]
                        )
                        await cursor.execute(
                            "UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?",
                            (channel, role.id, interaction.getGuild().id),
                        )
                    else:
                        content += bot.translator.getLocalString(interaction, "welcomeNoRole", [])
                        await cursor.execute(
                            "UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?",
                            (channel, 0, interaction.getGuild().id),
                        )

                await bot.connection.commit()
                await cursor.close()

                await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "welcome", "manage guild")
        else:
            await dmUnavailable(interaction, "welcome")


async def languageFunction(bot, interaction: ContextAdapter, language: app_commands.Choice[str]):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                cursor = await bot.connection.cursor()
                await cursor.execute(
                    "UPDATE dis_guild SET guild_locale = ? WHERE guild_id = ?",
                    (language, interaction.getGuild().id),
                )
                await bot.connection.commit()
                await cursor.close()
                bot.translator.updateCache(interaction.getGuild().id, language)

                content = bot.translator.getLocalString(interaction, "newLanguage", [])
                await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "language", "manage guild")
        else:
            await dmUnavailable(interaction, "language")


async def announceFunction(
    bot, interaction: ContextAdapter, channel: discord.TextChannel, message: str
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                if interaction.getAuthor().id == int(os.environ["OWNER_ID"]):
                    authorCredit = ""
                else:
                    authorCredit = bot.translator.getLocalString(
                        interaction,
                        "announceAuthor",
                        [("user", interaction.getAuthor().mention)],
                    )

                if channel.guild.id == interaction.getGuild().id:
                    message = await channel.send(authorCredit + message)
                    content = bot.translator.getLocalString(interaction, "announceLink", [])
                    await interaction.sendMessage(content=content + message.jump_url)
                else:
                    content = bot.translator.getLocalString(interaction, "channelGuild", [])
                    await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "announce", "manage guild")
        else:
            await dmUnavailable(interaction, "announce")


async def togglelevelsFunction(bot, interaction: ContextAdapter, toggle: int):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                cursor = await bot.connection.cursor()
                await cursor.execute(
                    "UPDATE dis_guild SET guild_levels_enabled = ? WHERE guild_id = ?",
                    (toggle, interaction.getGuild().id),
                )
                await bot.connection.commit()
                await cursor.close()

                if toggle == 1:
                    content = bot.translator.getLocalString(interaction, "togglelevelsEnabled", [])
                    await interaction.sendMessage(content=content)
                else:
                    content = bot.translator.getLocalString(
                        interaction, "togglelevelsDisabled", []
                    )
                    await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "togglelevels", "manage guild")
        else:
            await dmUnavailable(interaction, "togglelevels")


async def giveawayFunction(
    bot,
    interaction: ContextAdapter,
    channel: discord.TextChannel,
    prize: str,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    role: discord.Role = None,
):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                # Convert to seconds
                duration = days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60
                if duration != 0:

                    # Check if channel on guild
                    channelOnGuild = False
                    for checkChannel in interaction.getGuild().text_channels:
                        if checkChannel.id == channel.id:
                            channelOnGuild = True

                    # If channel is found
                    if channelOnGuild:
                        embed = GiveawayEmbed(interaction, duration, prize, role, bot.translator)

                        # Try sending the giveaway
                        try:
                            givMess = await channel.send(
                                embed=embed,
                                view=GiveawayView(
                                    translator=bot.translator, interaction=interaction
                                ),
                            )
                        # If channel not reachable
                        except discord.errors.Forbidden:
                            content = bot.translator.getLocalString(
                                interaction, "kannaMissPerms", []
                            )
                            await interaction.sendMessage(content=content)

                        content = bot.translator.getLocalString(interaction, "giveawayCreated", [])
                        await interaction.sendMessage(content=content)

                        cursor = await bot.connection.cursor()
                        if role != None and role.name != "@everyone":
                            await cursor.execute(
                                "INSERT INTO giv_giveaway(giv_message_id, giv_prize, giv_channel_id, giv_end_date, giv_role_id) VALUES (?,?,?,?,?)",
                                (
                                    givMess.id,
                                    prize,
                                    channel.id,
                                    time.time() + duration,
                                    role.id,
                                ),
                            )
                        else:
                            await cursor.execute(
                                "INSERT INTO giv_giveaway(giv_message_id, giv_prize, giv_channel_id, giv_end_date, giv_role_id) VALUES (?,?,?,?,?)",
                                (
                                    givMess.id,
                                    prize,
                                    channel.id,
                                    time.time() + duration,
                                    0,
                                ),
                            )
                        await bot.connection.commit()
                        await cursor.close()

                    else:
                        content = bot.translator.getLocalString(interaction, "channelGuild", [])
                        await interaction.sendMessage(content=content)
                else:
                    content = bot.translator.getLocalString(interaction, "giveawayNoDuration", [])
                    await interaction.sendMessage(content=content)
            else:
                await missing_perms(bot, interaction, "giveaway", "manage guild")
        else:
            await dmUnavailable(interaction, "giveaway")


async def editlevelsFunction(bot, interaction: ContextAdapter):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:

                embed = LevelListEmbed(bot, interaction)
                view = LevelListView(bot, interaction)
                await interaction.sendMessage(embed=embed, view=view)

            else:
                await missing_perms(bot, interaction, "giveaway", "manage guild")
        else:
            await dmUnavailable(interaction, "giveaway")


async def addlevelFunction(bot, interaction: ContextAdapter, level: int, role: discord.Role):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getAuthor().guild_permissions.manage_guild:
                if role.name == "@everyone":
                    content = bot.translator.getLocalString(interaction, "addlevelEveryone", [])
                    await interaction.sendMessage(content=content, ephemeral=True)
                    return

                cursor = await bot.connection.cursor()
                try:
                    await cursor.execute(
                        "INSERT INTO gld_reward (guild_id, rew_level, rew_role) VALUES (?,?,?)",
                        (interaction.getGuild().id, level, role.id),
                    )
                except sqlite3.IntegrityError:
                    await cursor.close()
                    content = bot.translator.getLocalString(
                        interaction, "addlevelFailure", [("level", str(level))]
                    )
                    await interaction.sendMessage(content=content, ephemeral=True)
                    return

                await bot.connection.commit()
                await cursor.close()

                content = bot.translator.getLocalString(
                    interaction,
                    "addlevelSuccess",
                    [("role", role.name), ("level", str(level))],
                )
                await interaction.sendMessage(content=content)

            else:
                await missing_perms(bot, interaction, "giveaway", "manage guild")
        else:
            await dmUnavailable(interaction, "giveaway")
