from traceback import format_exc

from connection import *
from prefix import *
from bot import *


async def setup_func(guild):
	cursor = await bot.connection.cursor()
	await cursor.execute("SELECT guild_id FROM dis_guild WHERE guild_id = ?", (guild.id, ))
	if await cursor.fetchone() == None:
		await cursor.execute("INSERT INTO dis_guild(guild_id, guild_prefix, guild_locale) VALUES(?, '!', 'en')", (guild.id, ))
	for user in guild.members:
		if not user.bot:
			await cursor.execute("SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (user.id, ))
			userInfos = await cursor.fetchone()
			if userInfos == None:
				await cursor.execute("INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)", (user.id, user.name))
			elif (user.name != userInfos[1]):
				await cursor.execute("UPDATE dis_user SET user_name = ? where user_id = ?", (user.name, user.id))

	await bot.connection.commit()
	await cursor.close()


@bot.event
async def on_command_error(context, error):
	context = ContextAdapter(context)
	if isinstance(error, commands.CommandInvokeError):
		error = error.original
	if isinstance(error, commands.CommandNotFound):
		return
	elif isinstance(error, discord.errors.Forbidden):
		try:
			content = bot.translator.getLocalString(context, "kannaMissPerms", [])
			await context.sendMessage(content = content)
			return
		except Exception as e:
				return


	me = await bot.fetch_user(os.environ['OWNER_ID'])
	await me.send(error)
	raise error



@bot.event
async def on_member_join(member):
	cursor = await bot.connection.cursor()
	await cursor.execute("SELECT guild_welcome_channel_id, guild_welcome_role_id FROM dis_guild WHERE guild_id = ?", (member.guild.id,))
	welcomeSettings = await cursor.fetchone()
	channel_ID = welcomeSettings[0]
	role_ID = welcomeSettings[1]
	if channel_ID != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID)
		if welcome_channel is not None:
			content = bot.translator.getLocalString(
			    member, "welcome", [("memberID", str(member.id))])
			await welcome_channel.send(content=content)

	if role_ID != 0:
		welcome_role: discord.Role = member.guild.get_role(role_ID)
		if welcome_role is not None:
			try:
				await member.add_roles(welcome_role, reason="Gave welcome role")
			except discord.errors.Forbidden as e:
				try:
					content = bot.translator.getLocalString(member, "errorWelcomeRole", [
					                                        ("guild", member.guild.name)])
					await member.guild.owner.send(content=content)
				except Exception:
					pass

	# Insert new member in database
	if not member.bot:
		await cursor.execute("SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (member.id, ))
		member_id = await cursor.fetchone()
		if member_id == None:
			await cursor.execute("INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)", (member.id, member.name))
		elif (member.name != member_id[1]):
			await cursor.execute("UPDATE dis_user SET user_name = ? WHERE user_id = ?", (member.name, member.id))
		await bot.connection.commit()
	await cursor.close()


@bot.event
async def on_member_remove(member):
	cursor = await bot.connection.cursor()
	await cursor.execute("SELECT guild_welcome_channel_ID FROM dis_guild WHERE guild_id = ?", (member.guild.id, ))
	channel_ID = await cursor.fetchone()
	await cursor.close()

	if channel_ID[0] != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID[0])
		if welcome_channel is not None:
			content = bot.translator.getLocalString(member, "goodbye", [(
			    "memberName", member.name + "#" + member.discriminator)])
			await welcome_channel.send(content=content)


@bot.event
async def on_guild_join(guild):
	await setup_func(guild)


@bot.event
async def on_message(message):
	if not message.author.bot:

		# Prefix
		if message.content.lower() == "ping":
			prefix = await get_pre(message)
			await message.channel.send("Pong! `" + str(int(bot.latency * 1000)) + "ms`\nPrefix : `" + prefix + "`")
		cursor = await bot.connection.cursor()

		# Levels
		if (message.guild is not None):
			await cursor.execute("SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?", (message.guild.id, ))
			enabled = await cursor.fetchone()
		else:
			enabled = [1]
		if enabled[0] == 1:
			await cursor.execute("SELECT user_xp, user_level FROM dis_user WHERE user_id = ?", (message.author.id, ))
			user_leveling = await cursor.fetchone()
			user_xp = user_leveling[0]
			user_level = user_leveling[1]
			user_xp += random.randint(30, 50)
			if user_xp > 500 * user_level:
				user_xp -= 500 * user_level
				user_level += 1
				await cursor.execute("UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, message.author.id))
				content = bot.translator.getLocalString(message, "levelUp", [(
				    "user", message.author.mention), ("number", str(user_level))])
				await message.channel.send(content=content)
			else:
				await cursor.execute("UPDATE dis_user SET user_xp = ? WHERE user_id = ?", (user_xp, message.author.id))

		await bot.connection.commit()
		await cursor.close()

		# Runs commands if it exists
		await bot.process_commands(message)


@bot.event
async def on_user_update(before: discord.User, after: discord.User):
	if (before.name != after.name):
		cursor = await bot.connection.cursor()
		await cursor.execute("UPDATE dis_user SET user_name = ? WHERE user_id = ?", (after.name, before.id))
		await bot.connection.commit()
		await cursor.close()


@bot.event
async def on_command_completion(ctx):
	if (not ctx.author.bot):
		cursor = await bot.connection.cursor()
		await cursor.execute("INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)", (ctx.command.name, ctx.author.id, time.time()))
		await bot.connection.commit()
		await cursor.close()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    interaction = ContextAdapter(interaction)



    if(isinstance(error, discord.app_commands.errors.CommandInvokeError)):
        error = error.original

    if (isinstance(error, discord.Forbidden)):
        content = bot.translator.getLocalString(interaction, "kannaMissPerms", [])
        await interaction.sendMessage(content = content)

    #Error report
    else:
        me = await bot.fetch_user(os.environ['OWNER_ID'])
        message = format_exc()
        if len(message) >= 2000:
            message = message.splitlines()
            middle = int(len(message)/2)

            await me.send('\n'.join(message[:middle]))
            await me.send('\n'.join(message[middle:]))
        else:
            await me.send(message)

        content = bot.translator.getLocalString(interaction, "kannaError", [])
        try:
            await interaction.sendMessage(content = content);
        except Exception as e:
            try:
                await interaction.followupSend(content = content, view = None, embed = None)
            except Exception:
                return
    return


@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command):
    interaction = ContextAdapter(interaction)
    if (not interaction.getAuthor().bot):
        cursor = await bot.connection.cursor()
        await cursor.execute("INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)", (command.name, interaction.getAuthor().id , time.time() ))


        #Levels
        if(interaction.getGuild() is not None):
            await cursor.execute("SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?", (interaction.getGuild().id, ))
            enabled = await cursor.fetchone()
        else:
            enabled = [1]
        if enabled[0] == 1:
            await cursor.execute("SELECT user_xp, user_level FROM dis_user WHERE user_id = ?", (interaction.getAuthor().id, ))
            user_leveling = await cursor.fetchone()
            user_xp = user_leveling[0]
            user_level = user_leveling[1]
            user_xp += random.randint(90,150)
            if user_xp > 500*user_level:
                user_xp -= 500*user_level
                user_level +=1
                await cursor.execute("UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, interaction.getAuthor().id))
                content = bot.translator.getLocalString(interaction, "levelUp", [("user", interaction.getAuthor().mention), ("number", str(user_level))])
                await interaction.getChannel().send(content = content)
            else:
                await cursor.execute("UPDATE dis_user SET user_xp = ? WHERE user_id = ?", (user_xp, interaction.getAuthor().id))


        await bot.connection.commit()
        await cursor.close()
