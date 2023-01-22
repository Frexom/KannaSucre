from connection import *
from prefix import *
from bot import *


sys.path.append("../ressources")



async def setup_func(guild):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute("SELECT guild_id FROM dis_guild WHERE guild_id = ?", (guild.id, ))
	if await cursor.fetchone() == None:
		await cursor.execute("INSERT INTO dis_guild(guild_id, guild_prefix, guild_locale) VALUES(?, '!', 'en')", (guild.id, ))
	for user in guild.members :
		if not user.bot:
			await cursor.execute("SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (user.id, ))
			userInfos = await cursor.fetchone()
			if userInfos == None:
				await cursor.execute("INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)", (user.id, user.name))
			elif(user.name != userInfos[1]):
				await cursor.execute("UPDATE dis_user SET user_name = ? where user_id = ?", (user.name, user.id))

	await connection.commit()
	await close_conn(connection, cursor)


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		error = error.original
	if isinstance(error, commands.CommandNotFound):
		return
	elif isinstance(error, discord.errors.Forbidden):
		try:
			content = bot.translator.getLocalString(ctx, "kannaMissPerms", [])
			await ctx.channel.send(content = content)
			return
		except Exception as e:
				return
	me = await bot.fetch_user(os.environ['OWNER_ID'])
	await me.send(error)
	raise error


@bot.event
async def on_member_join(member):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute("SELECT guild_welcome_channel_id, guild_welcome_role_id FROM dis_guild WHERE guild_id = ?", (member.guild.id,))
	welcomeSettings = await cursor.fetchone()
	channel_ID = welcomeSettings[0]
	role_ID = welcomeSettings[1]
	if channel_ID != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID)
		if welcome_channel is not None:
			content = bot.translator.getLocalString(member, "welcome", [("memberID", str(member.id))])
			await welcome_channel.send(content = content)

	if role_ID != 0:
		welcome_role: discord.Role = member.guild.get_role(role_ID)
		if welcome_role is not None:
			try:
				await member.add_roles(welcome_role, reason = "Gave welcome role")
			except discord.errors.Forbidden as e:
				try:
					content = bot.translator.getLocalString(member, "errorWelcomeRole", [("guild", member.guild.name)])
					await member.guild.owner.send(content = content)
				except Exception:
					pass

	#Insert new member in database
	if not member.bot:
		await cursor.execute("SELECT user_id, user_name FROM dis_user WHERE user_id = ?", (member.id, ))
		member_id = await cursor.fetchone()
		if member_id == None:
			await cursor.execute("INSERT INTO dis_user(user_id, user_name) VALUES(?, ?)", (member.id, member.name))
			if(member.name != member_id[1]):
				await cursor.execute("UPDATE dis_user SET user_name = ? WHERE user_id = ?", (member.name, member.id))
			await connection.commit()
	await close_conn(connection, cursor)


@bot.event
async def on_member_remove(member):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute("SELECT guild_welcome_channel_ID FROM dis_guild WHERE guild_id = ?", (member.guild.id, ))
	channel_ID = await cursor.fetchone()
	await close_conn(connection, cursor)

	if channel_ID[0] != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID[0])
		if welcome_channel is not None:
			content = bot.translator.getLocalString(member, "goodbye", [("memberName", member.name+"#"+member.discriminator)])
			await welcome_channel.send(content = content)


@bot.event
async def on_guild_join(guild):
	await setup_func(guild)


@bot.event
async def on_message(message):
	if not message.author.bot :

		#Prefix
		if message.content.lower() == "ping":
			prefix = await get_pre(message)
			await message.channel.send("Pong! `" + str(int(bot.latency * 1000)) + "ms`\nPrefix : `" + prefix + "`")
		connection, cursor = await get_conn("./files/ressources/bot.db")

		#Levels
		if(message.guild is not None):
			await cursor.execute("SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?", (message.guild.id, ))
			enabled = await cursor.fetchone()
		else:
			enabled = [1]
		if enabled[0] == 1:
			await cursor.execute("SELECT user_xp, user_level FROM dis_user WHERE user_id = ?", (message.author.id, ))
			user_leveling = await cursor.fetchone()
			user_xp = user_leveling[0]
			user_level = user_leveling[1]
			user_xp += random.randint(30,50)
			if user_xp > 500*user_level:
				user_xp -= 500*user_level
				user_level +=1
				await cursor.execute("UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, message.author.id))
				content = bot.translator.getLocalString(message, "levelUp", [("user", message.author.mention), ("number", str(user_level))])
				await message.channel.send(content = content)
			else:
				await cursor.execute("UPDATE dis_user SET user_xp = ? WHERE user_id = ?", (user_xp, message.author.id))

		await connection.commit()
		await close_conn(connection, cursor)

		#Runs commands if it exists
		await bot.process_commands(message)

@bot.event
async def on_user_update(before: discord.User, after: discord.User):
	if(before.name != after.name):
		connection, cursor = await get_conn("./files/ressources/bot.db")
		await cursor.execute("UPDATE dis_user SET user_name = ? WHERE user_id = ?", (after.name, before.id))
		await connection.commit()
		await close_conn(connection, cursor)


@bot.event
async def on_command_completion(ctx):
	if(not ctx.author.bot):
		connection, cursor = await get_conn("./files/ressources/bot.db")
		await cursor.execute("INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)", (ctx.command.name, ctx.author.id, time.time() ))
		await connection.commit()
		await close_conn(connection, cursor)
