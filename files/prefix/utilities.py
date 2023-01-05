from mentions import *
from prefix import *
from bot import *

sys.path.append("../ressources")


@bot.command(name="dice")
async def dice(ctx):
    if not ctx.author.bot :
        words = ctx.message.content.split(" ")
        if len(words) > 1 and words[1].isdecimal() and int(words[1]) > 0:
            max = ctx.message.content.split(" ")[1]
            number = random.randint(1, int(max))
            content = bot.translator.getLocalString(ctx, "diceRoll", [("randomNumber", number), ("maxNumber", max)])
            await ctx.send(content = content)
        else:
            prefix = str(await get_pre(ctx))
            await ctx.send("```" + str(prefix) + "dice *number>0*```")


@bot.command(name="servericon")
async def servericon(ctx):
    if not ctx.author.bot :
        if(ctx.guild.icon is not None):
            await ctx.send(ctx.guild.icon.url)
        else:
            content = bot.translator.getLocalString(ctx, "servericon", [])
            await ctx.send(content = content)


@bot.command(name="usericon")
async def usericon(ctx):
    if not ctx.author.bot :
        user = get_target(ctx)
        if(user.display_avatar is not None):
            await ctx.send(user.display_avatar.url)
        else:
            content = bot.translator.getLocalString(ctx, "servericon", [])
            await ctx.send(content)

@bot.command(name="supportserver")
async def supportserver(ctx):
    if not ctx.author.bot:
        link = os.environ['SUPPORTSERVERLINK']
        content = bot.translator.getLocalString(ctx, "supportServer", [])
        await ctx.channel.send(content + link)


@bot.command(name="help")
async def help(ctx):
    if not ctx.author.bot :
        connection, cursor = await get_conn("./files/ressources/bot.db")
        message_list = ctx.message.content.split(" ")
        if len(message_list) < 2:

            categories = []
            categories.append(bot.translator.getLocalString(ctx, "helpCatAdmin", []))
            categories.append(bot.translator.getLocalString(ctx, "helpCatMod", []))
            categories.append(bot.translator.getLocalString(ctx, "helpCatUtil", []))
            categories.append(bot.translator.getLocalString(ctx, "helpCatMisc", []))

            await cursor.execute("SELECT com_name, com_short, cat_category FROM com_command ORDER BY cat_category, com_name")
            commands = await cursor.fetchall()
            await close_conn(connection, cursor)

            title = bot.translator.getLocalString(ctx, "helpBigTitle", [])
            embed = discord.Embed(title=title, colour=discord.Colour(0x635f))
            embed.set_thumbnail(url=bot.user.avatar.url)
            index = 0
            for i in range(4):
                content = ""
                while(index < len(commands) and commands[index][2] == i+1):
                    comShort = bot.translator.getLocalString(ctx, commands[index][0]+"Short", [])
                    content += "`" + commands[index][0] +    "` : " + comShort +"\n"
                    index += 1;
                embed.add_field(name=categories[i], value=content, inline=False)
            await ctx.send(embed=embed)
        else:
            await cursor.execute("SELECT com_name, com_desc, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM com_command")
            commands = await cursor.fetchall()
            await close_conn(connection, cursor)
            parameter = message_list[1]
            successful = False
            for i in range(len(commands)):
                if commands[i][0] == parameter:
                    prefix = str(await get_pre(ctx))
                    title = bot.translator.getLocalString(ctx, "helpTitle", [("command", commands[i][0])])
                    embed = discord.Embed(title= title, colour=discord.Colour(0x635f), description=commands[i][1])
                    embed.set_thumbnail(url=bot.user.avatar.url)
                    name = bot.translator.getLocalString(ctx, "helpUserPerms", [])
                    embed.add_field(name=name, value="`" + commands[i][3] + "`", inline = True)
                    name = bot.translator.getLocalString(ctx, "helpKannaPerms", [])
                    embed.add_field(name=name, value="`" + commands[i][4] + "`", inline = True)
                    if commands[i][5] is not None:
                        answer = bot.translator.getLocalString(ctx, "helpNo", [])
                        if int(commands[i][5]) == 1:
                            answer = bot.translator.getLocalString(ctx, "helpYes", [])
                        name = bot.translator.getLocalString(ctx, "helpMorePerms", [])
                        embed.add_field(name=name, value= "```" + answer + "```", inline = False)
                    name = bot.translator.getLocalString(ctx, "helpExample", [])
                    embed.add_field(name=name, value= "```" + prefix + commands[i][2] + "```", inline = False)
                    await ctx.send(embed=embed)
                    successful = True
            if successful == False :
                content = bot.translator.getLocalString(ctx, "helpNoCommand", [("name", parameter)])
                await ctx.send(content=content)
