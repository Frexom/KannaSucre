import sys
sys.path.append("./files/resources")
sys.path.append("./files/functions")

from bot import *

from eventsFunctions import *

@bot.event
async def on_ready():

    #Adding cogs
    path="files.cogs"
    for filename in os.listdir("files/cogs/"):
        if os.path.isfile(f"files/cogs/{filename}"):
            await bot.load_extension(f"{path}.{filename[:-3]}")

    #Cog already loaded (while reconnecting)
    #except discord.errors.ClientException:
        #pass

    #Downtime database update
    for i in range(len(bot.guilds)):
        await setup_func(bot.guilds[i])

    #Appearance
    game = discord.Game('Now with slash commands!')
    await bot.change_presence(status=discord.Status.online, activity=game)
    random.seed(time.time())
    try:
        checkEndedGiveaways.start()
    except RuntimeError:
        pass
    print("Bot is ready")


@tasks.loop(seconds=30)
async def checkEndedGiveaways():
    connection, cursor = await get_conn("./files/resources/bot.db")
    await cursor.execute("""
    SELECT giv_message_id, giv_channel_id, giv_prize,
    (
        SELECT user_id FROM giv_entry WHERE giv_giveaway.giv_message_id = giv_message_id ORDER BY RANDOM() LIMIT 1
    ) as giv_winner,
	(
        SELECT COUNT(*) FROM giv_entry WHERE giv_giveaway.giv_message_id = giv_message_id
    ) as giv_count
    FROM giv_giveaway WHERE giv_ended = 0 and giv_end_date < STRFTIME('%s')
    """)
    giveaways = await cursor.fetchall()

    for giveaway in giveaways :
        channel = bot.get_channel(giveaway[1])
        message = await channel.fetch_message(giveaway[0])

        if(giveaway[3] is None):
            content = bot.translator.getLocalString(channel, "giveawayLost", [])
        else:
            content = bot.translator.getLocalString(channel, "giveawayWon", [("number", str(giveaway[4])), ("userId", str(giveaway[3])), ("prize", str(giveaway[2]))])
        await channel.send(content = content, reference=message)
        await cursor.execute("UPDATE giv_giveaway SET giv_ended = 1 WHERE giv_message_id = ?", (giveaway[0], ))

    await connection.commit()
    await close_conn(connection, cursor)


bot.run(os.environ['TOKEN'])
