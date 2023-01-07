from mentions import *
from prefix import *
from perms import *

sys.path.append("../ressources")


@bot.command(name="prune")
async def prune(ctx):
    if not ctx.author.bot :
        if(ctx.guild is not None):
            await ctx.channel.typing()
            if ctx.message.author.guild_permissions.manage_messages:
                user = get_mention(ctx)
                if user is not None:
                    if not user.guild_permissions.manage_messages or user.bot:
                        def checkUser(m):
                            return m.author == user
                        mess_count = 0
                        for channel in ctx.guild.text_channels:
                            mess_count += len(await channel.purge(limit = 200, check = checkUser))
                        content = bot.translator.getLocalString(ctx, "pruneUser", [("number", str(mess_count)), ("user", user.name), ("guild", ctx.guild.name)])
                        await ctx.send(content = content, delete_after=5)
                        await ctx.author.send(content = content)
                    else:
                        await lack_perms(ctx, "prune")
                else:
                    prefix = str(await get_pre(ctx))
                    await ctx.send("```" + str(prefix) + "prune *mention targeted user*```")
            else:
                await missing_perms(ctx, "prune", "manage messages")
        else:
            await dmUnavailable(ctx, "prune")


@bot.command(name="clear")
async def clear(ctx):
    if not ctx.author.bot :
        if(ctx.guild is not None):
            if ctx.message.author.guild_permissions.manage_messages:
                number = ctx.message.content.split(" ")
                if len(number) > 1 and number[1].isdecimal():
                    number = int(number[1]) +1
                    if number < 52:
                        mess_count = len(await ctx.channel.purge(limit = number))
                        content = bot.translator.getLocalString(ctx, "clearMessages", [("number", mess_count)])
                        await ctx.send(content = content, delete_after=5)
                    else:
                        content = bot.translator.getLocalString(ctx, "clearMore", [])
                        await ctx.send(content = content)
                else:
                    prefix = str(await get_pre(ctx))
                    await ctx.send("```" + str(prefix) + "clear *number of messages*```")
            else:
                await missing_perms(ctx, "clear", "manage messages")
        else:
            await dmUnavailable(ctx, "clear")


@bot.command(name="kick")
async def kick(ctx):
    if not ctx.author.bot :
        if(ctx.guild is not None):
            if ctx.message.author.guild_permissions.kick_members:
                reason = ctx.message.content.split(" ")
                if len(ctx.message.mentions) > 0 or (len(reason) > 1 and reason[1].isdecimal() and len(reason[1]) > 15):
                    if reason[1].isdecimal():
                        member = ctx.guild.get_member(int(reason[1]))
                    else:
                        member = ctx.message.mentions[0]
                        reason = ' '.join(reason[2:])
                    if not member.guild_permissions.kick_members:
                        if reason != "":
                            content = bot.translator.getLocalString(ctx, "kickReason", [("guild", ctx.guild.name), ("reason", reason)])
                            await member.send(content = content)
                        else:
                            content = bot.translator.getLocalString(ctx, "kickNoReason", [("guild", ctx.guild.name)])
                            await member.send(content = content)
                        await member.kick()
                        await ctx.message.add_reaction("\u2705")
                    else:
                        await lack_perms(ctx, "kick")
                else:
                    prefix = str(await get_pre(ctx))
                    await ctx.send("```" + str(prefix) + "kick *mention target/target ID*```")
            else:
                await missing_perms(ctx, "kick", "kick members")
        else:
            await dmUnavailable(ctx, "kick")
