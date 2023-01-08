from connection import *
from prefix import *
from bot import *

sys.path.append("../ressources")



@bot.command(name="preview")
@commands.is_owner()
async def preview(ctx):
    message_list = ctx.message.content.split(" ")[1:]
    message = " ".join(message_list)
    await ctx.send(message)


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


@bot.command(name="rules")
@commands.is_owner()
async def preview(ctx):
    e = discord.Embed(title = ctx.guild.name + " rules", description = "Please note that any violation of those rules will be likely to result in a ban, if justified.\n\n\n")
    e.add_field(name = "Rule :one: : Respect", inline = False, value="Respect eachother, everyone here is considered equal, regardless of their gender, sexuality and origin. Do not discrimiate, discomfort or insult anyone here.\n\n\n")
    e.add_field(name = "Rule :two: : NSFW/Spam", inline = False, value="NSFW and spam are here strictly prohibed, this server must be able to welcome people regardless of their age.\n\n\n")
    e.add_field(name = "Rule :three: : Channels", inline = False, value="Respect the use of each channel, you can read a channel's description to see what is allowed and what isn't.")
    e.add_field(name = "Rule :four: : Profile", inline = False, value="No offensive profile picture or name. No one should be seeing offensive or sensitive content while clicking your profile.")
    e.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.channel.send(embed = e)

@bot.command(name="fetch")
@commands.is_owner()
async def fetch(ctx):
    await ctx.send("Working!")
    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT user_id FROM dis_user")
    users = await cursor.fetchall()
    for user in users:
        userObj = await bot.fetch_user(user[0])
        if(userObj is not None):
            print(userObj.name)
            await cursor.execute("UPDATE dis_user SET user_name = ? WHERE user_id = ?", (userObj.name, userObj.id))
    await connection.commit()
    await close_conn(connection, cursor)
    print("Done!")
    await ctx.send("Done!")
