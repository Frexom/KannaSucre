from connection import *
from prefix import *
from bot import *


sys.path.append("../ressources")



async def setup_func(guild):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild.id, ))
	if await cursor.fetchone() == None:
		await cursor.execute("INSERT INTO guilds(guild_id, guild_prefix) VALUES(?, '!')", (guild.id, ))
		for user in guild.members :
			if not user.bot:
				await cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id, ))
				if await cursor.fetchone() == None:
					await cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user.id, ))
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
				await ctx.channel.send("I don't have enough permissions to do that!")
				return
		except Exception as e:
				return
	me = await bot.fetch_user(os.environ['OWNER_ID'])
	await me.send(error)
	raise error


@bot.event
async def on_member_join(member):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute( "SELECT guild_welcome_channel_id FROM guilds WHERE guild_id = ?", (member.guild.id,))
	channel_ID = await cursor.fetchone()
	channel_ID = channel_ID[0]
	if channel_ID != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID)
		await welcome_channel.send("<@" + str(member.id) + "> joined the server! Yayy!!")

	if not member.bot:
		await cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (member.id, ))
		member_id = await cursor.fetchone()
		if member_id == None:
			await cursor.execute("INSERT INTO users(user_id) VALUES(?)", (int(member.id), ))
			await connection.commit()
	await close_conn(connection, cursor)


@bot.event
async def on_member_remove(member):
	connection, cursor = await get_conn("./files/ressources/bot.db")
	await cursor.execute("SELECT guild_welcome_channel_ID FROM guilds WHERE guild_id = ?", (member.guild.id, ))
	channel_ID = await cursor.fetchone()
	if channel_ID[0] != 0:
		welcome_channel: discord.TextChannel = bot.get_channel(channel_ID[0])
		await welcome_channel.send(str(member) + " left the server. :(")
	await close_conn(connection, cursor)


@bot.event
async def on_guild_join(guild):
	await setup_func(guild)


@bot.event
async def on_message(message):
	if not message.author.bot :
		try:
			prefix = await get_pre(message)
			if message.content.lower() == "ping":
				await message.channel.send("Pong! `" + str(int(bot.latency * 1000)) + "ms`\nPrefix : `" + prefix + "`")
			connection, cursor = await get_conn("./files/ressources/bot.db")
			await cursor.execute("SELECT guild_lengthlimit FROM guilds WHERE guild_id = ?", (message.guild.id, ))
			limit = await cursor.fetchone()
			if limit[0] != None and len(message.content) > limit[0] :
				await message.author.send("Your message has been deleted since it's too long for the server, try to short it down to **" + str(limit[0]) + "** characters.\nHere is your message :\n\n" + str(message.content))
				await message.delete()
			await cursor.execute("SELECT user_xp, user_level FROM users WHERE user_id = ?", (message.author.id, ))
			user_leveling = await cursor.fetchone()
			user_xp = user_leveling[0]
			user_level = user_leveling[1]
			user_xp += random.randint(30,50)
			if user_xp > 500*user_level:
				user_xp -= 500*user_level
				user_level +=1
				await cursor.execute("UPDATE users SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, message.author.id))
				await message.channel.send("Congratulations <@" + str(message.author.id) + ">, you are now level " + str(user_level) + "!")
			else:
				await cursor.execute("UPDATE users SET user_xp = ? WHERE user_id = ?", (user_xp, message.author.id))
			await connection.commit()
			await close_conn(connection, cursor)
			await bot.process_commands(message)
		except Exception as e:
			if "50013" not in str(e):
				raise e
