import os
import random
import time

import discord
from discord.ext import commands

from src.resources.adapter import ContextAdapter
from src.resources.prefix import Prefix


async def setup_func(bot, guild):
    cursor = await bot.connection.cursor()
    await cursor.execute("SELECT guild_id FROM dis_guild WHERE guild_id = ?", (guild.id,))
    if await cursor.fetchone() == None:
        await cursor.execute(
            "INSERT INTO dis_guild(guild_id, guild_prefix, guild_locale) VALUES(?, '!', 'en')",
            (guild.id,),
        )
    for user in guild.members:
        if not user.bot:
            global_name = user.global_name if user.global_name is not None else user.name

            await cursor.execute(
                "SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (user.id,)
            )
            userInfos = await cursor.fetchone()
            if userInfos == None:
                await cursor.execute(
                    "INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)",
                    (user.id, global_name),
                )
            elif global_name != userInfos[1]:
                await cursor.execute(
                    "UPDATE dis_user SET user_name = ? where user_id = ?",
                    (global_name, user.id),
                )

            await cursor.execute(
                "SELECT user_id FROM gld_level WHERE user_id = ? AND guild_id = ?",
                (user.id, guild.id),
            )
            userInfos = await cursor.fetchone()
            if userInfos == None:
                await cursor.execute(
                    "INSERT INTO gld_level(user_id, guild_id) VALUES(?, ?)",
                    (user.id, guild.id),
                )

    await bot.connection.commit()
    await cursor.close()


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        context = ContextAdapter(context)
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, discord.errors.Forbidden):
            try:
                content = self.bot.translator.getLocalString(context, "kannaMissPerms", [])
                await context.sendMessage(content=content)
                return
            except Exception as e:
                return

        me = await self.bot.fetch_user(os.environ["OWNER_ID"])
        await me.send(error)
        raise error

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cursor = await self.bot.connection.cursor()
        await cursor.execute(
            "SELECT guild_welcome_channel_id, guild_welcome_role_id FROM dis_guild WHERE guild_id = ?",
            (member.guild.id,),
        )
        welcomeSettings = await cursor.fetchone()
        channel_ID = welcomeSettings[0]
        role_ID = welcomeSettings[1]
        if channel_ID != 0:
            welcome_channel: discord.TextChannel = self.bot.get_channel(channel_ID)
            if welcome_channel is not None:
                content = self.bot.translator.getLocalString(
                    member, "welcome", [("memberID", str(member.id))]
                )
                await welcome_channel.send(content=content)

        if role_ID != 0:
            welcome_role: discord.Role = member.guild.get_role(role_ID)
            if welcome_role is not None:
                try:
                    await member.add_roles(welcome_role, reason="Gave welcome role")
                except discord.errors.Forbidden as e:
                    try:
                        content = self.bot.translator.getLocalString(
                            member, "errorWelcomeRole", [("guild", member.guild.name)]
                        )
                        await member.guild.owner.send(content=content)
                    except Exception:
                        pass

        # Insert new member in database
        if not member.bot:
            global_name = member.global_name if member.global_name is not None else user.name

            await cursor.execute(
                "SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (member.id,)
            )
            member_id = await cursor.fetchone()
            if member_id == None:
                await cursor.execute(
                    "INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)",
                    (member.id, global_name),
                )

            elif global_name != member_id[1]:
                await cursor.execute(
                    "UPDATE dis_user SET user_name = ? WHERE user_id = ?",
                    (global_name, member.id),
                )

            await cursor.execute(
                "SELECT user_id FROM gld_level WHERE user_id = ? AND guild_id = ?",
                (member.id, member.guild.id),
            )
            userInfos = await cursor.fetchone()
            if userInfos == None:
                await cursor.execute(
                    "INSERT INTO gld_level(user_id, guild_id) VALUES(?, ?)",
                    (member.id, member.guild.id),
                )

            await self.bot.connection.commit()
        await cursor.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        cursor = await self.bot.connection.cursor()
        await cursor.execute(
            "SELECT guild_welcome_channel_ID FROM dis_guild WHERE guild_id = ?",
            (member.guild.id,),
        )
        channel_ID = await cursor.fetchone()
        await cursor.close()

        if channel_ID[0] != 0:
            welcome_channel: discord.TextChannel = self.bot.get_channel(channel_ID[0])
            if welcome_channel is not None:
                content = self.bot.translator.getLocalString(
                    member,
                    "goodbye",
                    [("memberName", f"`{member.name}`")],
                )
                await welcome_channel.send(content=content)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await setup_func(self.bot, guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:

            # Prefix
            if message.content.lower() == "ping":
                prefix = Prefix.get_prefix(message)
                await message.channel.send(
                    "Pong! `"
                    + str(int(self.bot.latency * 1000))
                    + "ms`\nPrefix : `"
                    + prefix
                    + "`"
                )
            cursor = await self.bot.connection.cursor()

            # Levels
            await cursor.execute(
                "SELECT user_xp, user_level FROM dis_user WHERE user_id = ?",
                (message.author.id,),
            )
            user_leveling = await cursor.fetchone()
            user_xp = user_leveling[0]
            user_level = user_leveling[1]
            extraXp = random.randint(30, 50)
            user_xp += extraXp
            if user_xp > 500 * user_level:
                user_xp -= 500 * user_level
                user_level += 1
            await cursor.execute(
                "UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?",
                (user_xp, user_level, message.author.id),
            )

            # Guild level
            if message.guild is not None:
                await cursor.execute(
                    "SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?",
                    (message.guild.id,),
                )
                enabled = await cursor.fetchone()
                if enabled[0] == 1:
                    await cursor.execute(
                        """
                    SELECT lev_xp, lev_level, IFNULL(
                    (
                        SELECT rew_role FROM gld_reward WHERE guild_id = gld_level.guild_id AND rew_level = gld_level.lev_level+1
                    ),0) as role_id
                    FROM gld_level
                    WHERE user_id = ? AND guild_id = ?""",
                        (
                            message.author.id,
                            message.guild.id,
                        ),
                    )
                    guildLeveling = await cursor.fetchone()
                    guildXP = guildLeveling[0]
                    guildLevel = guildLeveling[1]

                    guildXP += extraXp
                    if guildXP > 500 * guildLevel:
                        guildXP -= 500 * guildLevel
                        guildLevel += 1

                        roleName = ""
                        success = True
                        levelRole: discord.Role = message.guild.get_role(guildLeveling[2])
                        if levelRole is not None:
                            try:
                                roleName = levelRole.name
                                await message.author.add_roles(
                                    levelRole, reason=f"Gave level {str(guildLevel)} role!"
                                )
                            except discord.errors.Forbidden as e:
                                success = False

                        if roleName == "" or not success:
                            content = self.bot.translator.getLocalString(
                                message,
                                "levelUp",
                                [
                                    ("user", message.author.mention),
                                    ("number", str(guildLevel)),
                                ],
                            )
                            if not success:
                                roleError = f"__Message from **{message.guild.name}** :__\n\nI do not have enough permissions to give the members their levelup role.\nIf you want to disable that feature, please run `/togglelevels disable` on **{message.guild.name}**.\nIf you want the feature to work, pelease make sure my role has the `manage roles` permission, and that my role is higher than the reward roles.\n This incident occured with the role `@{roleName}` at level {guildLevel}."
                                try:
                                    await message.guild.owner.send(content=roleError)
                                except Exception as e:
                                    pass
                        else:
                            content = self.bot.translator.getLocalString(
                                message,
                                "levelUpRole",
                                [
                                    ("user", message.author.mention),
                                    ("number", str(guildLevel)),
                                    ("role", roleName),
                                ],
                            )
                        await message.channel.send(content=content)

                    await cursor.execute(
                        "UPDATE gld_level SET lev_xp = ?, lev_level = ? WHERE user_id = ? AND guild_id = ?",
                        (guildXP, guildLevel, message.author.id, message.guild.id),
                    )

            await self.bot.connection.commit()
            await cursor.close()

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if (before.global_name != after.global_name) or (before.name != after.name):
            cursor = await self.bot.connection.cursor()
            global_name = after.global_name if after.global_name is not None else user.name
            await cursor.execute(
                "UPDATE dis_user SET user_name = ? WHERE user_id = ?",
                (after.global_name, before.id),
            )
            await self.bot.connection.commit()
            await cursor.close()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if not ctx.author.bot:
            cursor = await self.bot.connection.cursor()
            await cursor.execute(
                "INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)",
                (ctx.command.name, ctx.author.id, time.time()),
            )
            await self.bot.connection.commit()
            await cursor.close()

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command):
        interaction = ContextAdapter(interaction)
        if not interaction.getAuthor().bot:
            cursor = await self.bot.connection.cursor()
            await cursor.execute(
                "INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)",
                (command.name, interaction.getAuthor().id, time.time()),
            )

            # Levels
            await cursor.execute(
                "SELECT user_xp, user_level FROM dis_user WHERE user_id = ?",
                (interaction.getAuthor().id,),
            )
            user_leveling = await cursor.fetchone()
            user_xp = user_leveling[0]
            user_level = user_leveling[1]
            extraXp = random.randint(90, 150)
            user_xp += extraXp
            if user_xp > 500 * user_level:
                user_xp -= 500 * user_level
                user_level += 1
            await cursor.execute(
                "UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?",
                (user_xp, user_level, interaction.getAuthor().id),
            )

            # Guild level
            if interaction.getGuild() is not None:
                await cursor.execute(
                    "SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?",
                    (interaction.getGuild().id,),
                )
                enabled = await cursor.fetchone()
                if enabled[0] == 1:
                    await cursor.execute(
                        """
                    SELECT lev_xp, lev_level, IFNULL(
                    (
                        SELECT rew_role FROM gld_reward WHERE guild_id = gld_level.guild_id AND rew_level = gld_level.lev_level+1
                    ),0) as role_id
                    FROM gld_level
                    WHERE user_id = ? AND guild_id = ?""",
                        (
                            interaction.getAuthor().id,
                            interaction.getGuild().id,
                        ),
                    )
                    guildLeveling = await cursor.fetchone()
                    guildXP = guildLeveling[0]
                    guildLevel = guildLeveling[1]

                    guildXP += extraXp
                    if guildXP > 500 * guildLevel:
                        guildXP -= 500 * guildLevel
                        guildLevel += 1

                        roleName = ""
                        success = True
                        levelRole: discord.Role = interaction.getGuild().get_role(guildLeveling[2])
                        if levelRole is not None:
                            try:
                                roleName = levelRole.name
                                await interaction.getAuthor().add_roles(
                                    levelRole, reason=f"Gave level {str(guildLevel)} role!"
                                )
                            except discord.errors.Forbidden as e:
                                success = False

                        if roleName == "" or not success:
                            content = self.bot.translator.getLocalString(
                                interaction,
                                "levelUp",
                                [
                                    ("user", interaction.getAuthor().mention),
                                    ("number", str(guildLevel)),
                                ],
                            )
                            if not success:
                                roleError = f"__Message from **{interaction.getGuild().name}** :__\n\nI do not have enough permissions to give the members their levelup role.\nIf you want to disable that feature, please run `/togglelevels disable` on **{interaction.getGuild().name}**.\nIf you want the feature to work, pelease make sure my role has the `manage roles` permission, and that my role is higher than the reward roles.\nThis incident occured with the role `@{roleName}` at level {guildLevel}."

                                try:
                                    await interaction.getGuild().owner.send(content=roleError)
                                except Exception as e:
                                    pass
                        else:
                            content = self.bot.translator.getLocalString(
                                interaction,
                                "levelUpRole",
                                [
                                    ("user", interaction.getAuthor().mention),
                                    ("number", str(guildLevel)),
                                    ("role", roleName),
                                ],
                            )
                        await interaction.getChannel().send(content=content)

                    await cursor.execute(
                        "UPDATE gld_level SET lev_xp = ?, lev_level = ? WHERE user_id = ? AND guild_id = ?",
                        (
                            guildXP,
                            guildLevel,
                            interaction.getAuthor().id,
                            interaction.getGuild().id,
                        ),
                    )

            await self.bot.connection.commit()
            await cursor.close()


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
