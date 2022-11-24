from connection import *
from prefix import *
from perms import *

sys.path.append("../ressources")


@bot.command(name="prefix")
async def prefix(ctx):
  if not ctx.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      prefix = ctx.message.content.split(" ")
      if len(prefix) > 1:
        prefix = prefix[1]
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("UPDATE guilds SET guild_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        t = Translator(ctx.guild.id, loadStrings=True)
        content = t.getLocalString("newPrefix", [("prefix", str(prefix))])
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
    if ctx.message.author.guild_permissions.ban_members:
      reason = ctx.message.content.split(" ")
      if len(ctx.message.mentions) > 0 or (len(reason) > 1 and reason[1].isdecimal() and len(reason[1]) > 15):
        t = Translator(ctx.guild.id, loadStrings = True)
        if reason[1].isdecimal():
          member = ctx.guild.get_member(int(reason[1]))
        else:
          member = ctx.message.mentions[0]
        if not member.guild_permissions.ban_members:
          reason = ' '.join(reason[2:])
          if not member.bot:
            if reason != "":
              content = t.getLocalString("banReason", [("guild", ctx.guild.name), ("reason", reason)])
              await member.send(content = content)
            else:
              content = t.getLocalString("banNoReason", [("guild", ctx.guild.name)])
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
    if ctx.message.author.guild_permissions.manage_guild:
      connection, cursor = await get_conn("./files/ressources/bot.db")
      message = ctx.message.content.split(" ")
      if len(ctx.message.channel_mentions) > 0 or len(message) > 1 and message[1] == str(0):
        if len(ctx.message.channel_mentions) > 0:
          channel = ctx.message.channel_mentions[0].id
        else:
          channel = 0
        await cursor.execute("UPDATE guilds SET guild_welcome_channel_id = ? WHERE guild_id=?", (channel, ctx.guild.id))
        await ctx.message.add_reaction("\u2705")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        await cursor.execute("SELECT guild_welcome_channel_id FROM guilds WHERE guild_id = ?", (ctx.guild.id, ))
        welcome = await cursor.fetchone()
        await close_conn(connection, cursor)
        welcome = welcome[0]
        prefix = str(await get_pre(ctx))
        if welcome != 0 :
          content = t.getLocalString("welcomeChannel", [("channel", channel)])
          await ctx.send(content = content)
        else :
          content = t.getLocalString("welcomeDisabled", [])
          await ctx.send(content = content)
    else:
      await missing_perms(ctx, "welcome", "manage guild")
