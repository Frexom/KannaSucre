import sys
sys.path.append("./files/ressources")
sys.path.append("./files/prefix")
sys.path.append("./files/slash")

from bot import *

from image_editing import *
from moderation import *
from utilities import *
from events import *
from admin import *
from owner import *
from poke import *
from fun import *

from slashModeration import *
from slashUtilities import *
from slashEvents import *
from slashAdmin import *
from slashImage import *
from slashOwner import *
from slashPoke import *
from slashFun import *



@bot.event
async def on_ready():

    #Adding cogs
    try:
        await bot.add_cog(slashModeration(bot))
        await bot.add_cog(slashUtilities(bot))
        await bot.add_cog(slashAdmin(bot))
        await bot.add_cog(slashImage(bot))
        await bot.add_cog(slashOwner(bot))
        await bot.add_cog(slashPoke(bot))
        await bot.add_cog(slashFun(bot))

    #Cog already loaded (while reconnecting)
    except discord.errors.ClientException:
        pass

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
    connection, cursor = await get_conn("./files/ressources/bot.db")
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
