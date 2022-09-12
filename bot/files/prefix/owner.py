from connection import *
from prefix import *
from bot import *

import sys
sys.path.append("../ressources")



@bot.command(name="preview")
@commands.is_owner()
async def preview(ctx):
    message_list = ctx.message.content.split(" ")[1:]
    message = " ".join(message_list)
    await ctx.send(message)

@bot.command(name="announce")
@commands.is_owner()
async def announce(ctx):
    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT guild_announcements_channel_ID FROM guilds")
    IDs = await cursor.fetchall()
    await close_conn(connection, cursor)
    message_list = ctx.message.content.split(" ")[1:]
    message = ""
    message = " ".join(message_list)
    counter = 0
    for i in range(len(IDs)):
        if IDs[i][0] != 0 and IDs[i][0] != None :
            counter += 1
            channel = bot.get_channel(IDs[i][0])
            await channel.send(message)
    await ctx.send("Announcement made on " + str(counter) + " guilds.")


@bot.command(name="sql")
@commands.is_owner()
async def sql(ctx):
    if not ctx.author.bot :
        connection, cursor = await get_conn("./files/ressources/bot.db")
        query = ctx.message.content[5:]
        if(query[0].lower() == "s"):
            await cursor.execute(query)
            await ctx.send("That went alright!")
            result = await cursor.fetchall()
            if result == None:
                await ctx.send("None")
            else:
                await ctx.send(result)
        else:
            channel = ctx.channel
            author = ctx.author

            def check(m):
                return m.content == 'y' and m.channel == channel and m.author == author

            await cursor.execute(query)
            await ctx.send(str(cursor.rowcount) + " rows affected.")

            try:
                await ctx.send("Do you want to commit?")
                msg = await bot.wait_for('message',    check=check, timeout = 10)
                if msg:
                    await connection.commit()
                    await ctx.channel.send("Commited.")

            except asyncio.TimeoutError:
                await ctx.send("Command timed out.")

        await close_conn(connection, cursor)


@bot.command(name="database")
@commands.is_owner()
async def database(ctx):
    await ctx.send(file=discord.File('files/ressources/bot.db'), delete_after=2)

@bot.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx):
    author = ctx.message.author
    channel = ctx.channel
    def check(m):
        return m.content == 'y' and m.channel == channel and m.author == author

    await ctx.send("Do you really want to shut down the bot?")
    try:
        msg = await bot.wait_for('message',    check=check, timeout = 5)
        if msg:
            await ctx.send("Shutting down...")
            print("Shutting down...")
            await asyncio.sleep(1)
            await bot.close()

    except asyncio.TimeoutError:
        await ctx.send("The bot did not shut down.(timeout)")


@bot.command(name = "sync")
@commands.is_owner()
async def syncCommands(ctx: discord.ext.commands.Context, guilds: commands.Greedy[discord.Object]):
    await ctx.send("Syncing...")
    guilds.append(discord.Object(id=os.environ['TESTGUILDID']))

    #Global sync
    synced = await ctx.bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands globally.")

    #Owner sync
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
