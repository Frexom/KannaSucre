from connection import *
from prefix import *
from perms import *

sys.path.append("../ressources")


@bot.command(name="prefix")
async def prefix(ctx):
  if not ctx.author.bot :
    if ctx.author.guild_permissions.manage_guild:
      prefix = ctx.message.content.split(" ")
      if len(prefix) > 1:
        prefix = prefix[1]
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("UPDATE dis_guild SET guild_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        content = bot.translator.getLocalString(ctx, "newPrefix", [("prefix", str(prefix))])
        await ctx.send(content = content)
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        prefix = str(await get_pre(ctx))
        await ctx.send("```" + str(prefix) + "prefix *new prefix*```")
    else:
      await missing_perms(ctx, "prefix", "manage guild")


@bot.command(name="ban")
async def ban(ctx):
  if not ctx.author.bot :
    if ctx.author.guild_permissions.ban_members:
      reason = ctx.message.content.split(" ")
      if len(ctx.message.mentions) > 0 or (len(reason) > 1 and reason[1].isdecimal() and len(reason[1]) > 15):
        if reason[1].isdecimal():
          member = ctx.guild.get_member(int(reason[1]))
        else:
          member = ctx.message.mentions[0]
        if not member.guild_permissions.ban_members:
          reason = ' '.join(reason[2:])
          if not member.bot:
            if reason != "":
              content = bot.translator.getLocalString(ctx, "banReason", [("guild", ctx.guild.name), ("reason", reason)])
              await member.send(content = content)
            else:
              content = bot.translator.getLocalString(ctx, "banNoReason", [("guild", ctx.guild.name)])
              await member.send(content = content)
          await member.ban()
          await ctx.message.add_reaction("\u2705")
        else:
          await lack_perms(ctx, "ban")
      else:
        prefix = str(await get_pre(ctx))
        await ctx.send("```" + str(prefix) + "ban *mention target/target ID* *reason(optional)*```")
    else:
        await missing_perms(ctx, "ban", "ban members")


@bot.command(name="welcome")
async def welcome(ctx):
    if not ctx.author.bot :
        if ctx.author.guild_permissions.manage_guild:

            connection, cursor = await get_conn("./files/ressources/bot.db")
            content = ""
            message = ctx.message

            if(len(message.channel_mentions) > 0):
                channel = message.channel_mentions[0].id
                content += bot.translator.getLocalString(ctx, "welcomeChannel", [("channel", channel)])
                content += "\n"

                if(len(message.role_mentions) > 0 and message.role_mentions[0].name != "@everyone"):
                    role = message.role_mentions[0]
                    content += f"The role `@{role.name}` will be given to new members!"
                    await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (channel, role.id, ctx.guild.id))
                else:
                    content += "No role will be given to new members."
                    await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (channel, 0, ctx.guild.id))

            else:
                content += bot.translator.getLocalString(ctx, "welcomeDisabled", [])
                await cursor.execute("UPDATE dis_guild SET guild_welcome_channel_id = ?, guild_welcome_role_id = ? WHERE guild_id=?", (0, 0, ctx.guild.id))

            await connection.commit()
            await close_conn(connection, cursor)

            await ctx.send(content = content)
        else:
            await missing_perms(ctx, "welcome", "manage guild")


@bot.command(name = "language")
async def language(ctx):
    if not ctx.author.bot:
        if ctx.author.guild_permissions.manage_guild:
            message = ctx.message.content.split(" ")
            locales = ['en', 'fr']
            if(len(message) >= 2 and message[1] in locales):
                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE dis_guild SET guild_locale = ? WHERE guild_id = ?", (message[1], ctx.guild.id))
                await connection.commit()
                bot.translator.updateCache(ctx.guild.id, message[1])

                content = bot.translator.getLocalString(ctx, "newLanguage", [])
                await ctx.send(content = content)
            else:
                prefix = str(await get_pre(ctx))
                await ctx.send("```" + str(prefix) + "language en/fr```")
        else:
            await missing_perms(ctx, "language", "manage guild")


@bot.command(name="announce")
async def announce(ctx):
    if ctx.author.guild_permissions.manage_guild:
        message = ctx.message.content.split(" ")
        channel = ctx.message.channel_mentions
        if(len(channel) >= 1 and len(message) >= 3):
            channel = channel[0]
            if(channel.guild.id == ctx.guild.id):
                if ctx.author.id == int(os.environ['OWNER_ID']):
                    authorCredit = ""
                else:
                    authorCredit = bot.translator.getLocalString(ctx, "announceAuthor", [("user", ctx.author.mention)])

                await channel.send(authorCredit + str(' '.join(message[2:])))
            else:
                content = bot.translator.getLocalString(ctx, "channelGuild", [])
                await ctx.send(content = content)
        else:
            prefix = str(await get_pre(ctx))
            await ctx.send("```" + str(prefix) + "announce *mention channel* *message*```")
    else:
        await missing_perms(ctx, "announce", "manage guild")

@bot.command(name="togglelevels")
async def toggleLevels(ctx):
    if not ctx.author.bot:
        if ctx.author.guild_permissions.manage_guild:
            message = ctx.message.content.split(" ")
            toggle = message[1]
            if(toggle.isnumeric() and (toggle == "0" or toggle == "1")):
                toggle = int(toggle)
                connection, cursor = await get_conn("./files/ressources/bot.db")
                await cursor.execute("UPDATE dis_guild SET guild_levels_enabled = ? WHERE guild_id = ?", (toggle, ctx.guild.id))
                await connection.commit()

                if toggle == 1:
                    content = bot.translator.getLocalString(ctx, "togglelevelsEnabled", [])
                    await ctx.send(content = content)
                else:
                    content = bot.translator.getLocalString(ctx, "togglelevelsDisabled", [])
                    await ctx.send(content = content)
            else:
                prefix = str(await get_pre(ctx))
                await ctx.send("```" + str(prefix) + "togglelevels 0 or 1```")
        else:
            await missing_perms(ctx, "announce", "manage guild")
