import discord
from discord.ext import commands
from connection import *
from perms import *
from prefix import *


async def prefix(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      prefix = ctx.message.content.split(" ")
      if len(prefix) > 1:
        prefix = prefix[1]
        connection, cursor = await get_conn()
        await cursor.execute("UPDATE guilds SET guild_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        await ctx.send("My prefix for this server now is `" + str(prefix) + "` :)")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        prefix = str(await get_pre(ctx))
        await ctx.send("```" + str(prefix) + "prefix *new prefix*```")
    else:
      await missing_perms(ctx, "prefix", "manage guild")

async def ban(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.ban_members:
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
              await member.send("you have been banned from **" + str(ctx.guild.name) + "**.\nReason : `" + reason + "`.")
            else:
              await member.send("You have been banned from **" + str(ctx.guild.name) + "**.\nNo reason given.")
          await member.ban()
          await ctx.message.add_reaction("\u2705")
        else:
          await lack_perms(ctx, "ban")
      else:
        prefix = str(await get_pre(ctx))
        await ctx.send("```" + str(prefix) + "ban *mention target/target ID* *reason(optional)*```")
    else:
        await missing_perms(ctx, "ban", "ban members")


async def welcome(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      connection, cursor = await get_conn()
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
          await ctx.send("The current welcome channel is <#" + str(welcome) + ">. If you want to change it, please use this command :\n" + "```" + str(prefix) + "welcome   *mention new welcome channel or 0 to disable*```")
        else :
          await ctx.send("There is not defined welcome channel defined for this server right now. If you want to set up one to see who enters and leaves your server, please use this command :\n" + "```" + str(prefix) + "welcome *mention new welcome channel*```")
    else:
      await missing_perms(ctx, "welcome", "manage guild")



async def announcements(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      connection, cursor = await get_conn()
      message = ctx.message.content.split(" ")
      if len(ctx.message.channel_mentions) > 0 or len(message) > 1 and message[1] == str(0):
        if len(ctx.message.channel_mentions) > 0:
          channel = ctx.message.channel_mentions[0].id
        else:
          channel = 0
        await cursor.execute("UPDATE guilds SET guild_announcements_channel_ID = ? WHERE guild_id=?",(channel, ctx.guild.id))
        await ctx.message.add_reaction("\u2705")
        await connection.commit()
        await close_conn(connection, cursor)
      else:
        await cursor.execute("SELECT guild_announcements_channel_ID FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
        announcements = await cursor.fetchone()
        await close_conn(connection, cursor)
        announcements = announcements[0]
        prefix = str(await get_pre(ctx))
        if announcements != 0 :
          await ctx.send("The current announcements channel is <#" + str(announcements) + ">. If you want to change it, please use this command :\n" + "```" + str(prefix) +   "announcements *mention new announcements channel or 0 to disable*```")
        else :
          await ctx.send("There is not defined announcements channel defined for this server right now. If you want to set up one to stay tuned with the latest KannaSucre News, please use this command :\n" + "```" + str(prefix) + "announcements *mention new announcements channel*```")
    else:
      await missing_perms(ctx, "announcements", "manage guild")


async def lengthlimit(ctx):
  if not ctx.message.author.bot :
    if ctx.message.author.guild_permissions.manage_guild:
      limit = ctx.message.content.split(" ")
      if len(limit) > 1 and limit[1].isdecimal():
        limit = limit[1]
        if limit.isdecimal() and int(limit) > 299:
          connection, cursor = await get_conn()
          await cursor.execute("UPDATE guilds SET guild_lengthlimit = ? WHERE guild_id = ?",(limit, ctx.guild.id))
          await ctx.send("The message character limit for this server now is **" +str(limit) + "** characters :)")
          await connection.commit()
          await close_conn(connection, cursor)
        else:
          await ctx.send("I'm sorry but the character limit must be at least 300 characters.")
      else:
        prefix = str(await get_pre(ctx))
        await ctx.send("```" + str(prefix) +"lengthlimit *characters limit*```")
    else:
      await missing_perms(ctx, "lengthlimit", "manage guild")
