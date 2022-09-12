from mentions import *
from prefix import *
from bot import *

sys.path.append("../ressources")


@bot.command(name="dice")
async def dice(ctx):
  if not ctx.author.bot :
    words = ctx.message.content.split(" ")
    if len(words) > 1 and words[1].isdecimal() and int(words[1]) > 0:
      i = ctx.message.content.split(" ")[1]
      number = random.randint(1, int(i))
      await ctx.send("Rolled **" + str(number) + "**!")
    else:
      prefix = str(await get_pre(ctx))
      await ctx.send("```" + str(prefix) + "dice *number>0*```")


@bot.command(name="servericon")
async def servericon(ctx):
  if not ctx.author.bot :
    await ctx.send(ctx.guild.icon.url or "This server does not have an icon.")


@bot.command(name="usericon")
async def usericon(ctx):
    if not ctx.author.bot :
        user = get_target(ctx)
        await ctx.send(user.display_avatar.url or "This user does not have an icon.")


@bot.command(name="help")
async def help(ctx):
  if not ctx.author.bot :
    connection, cursor = await get_conn("./files/ressources/bot.db")
    message_list = ctx.message.content.split(" ")
    if len(message_list) < 2:
      categories = ["__Admin commands :__ \n\n", "\n\n__Moderation commands :__ \n\n", "\n\n__Utilities commands :__ \n\n", "\n\n__Miscellaneous/Fun commands :__ \n\n"]
      await cursor.execute("SELECT com_name, com_short, cat_category FROM commands ORDER BY cat_category, com_name")
      commands = await cursor.fetchall()
      await close_conn(connection, cursor)
      content = ""
      index = 0
      for i in range(4):
        content += categories[i]
        while(index < len(commands) and commands[index][2] == i+1):
          content += "`" + commands[index][0] +  "` : " + commands[index][1] +"\n"
          index += 1;
      embed = discord.Embed(title= "Kannasucre help : ", colour=discord.Colour(0x635f))
      embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
      embed.add_field(name="** **", value=content)
      await ctx.send(embed=embed)
    else:
      await cursor.execute("SELECT com_name, com_desc, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM commands")
      commands = await cursor.fetchall()
      await close_conn(connection, cursor)
      parameter = message_list[1]
      successful = False
      for i in range(len(commands)):
        if commands[i][0] == parameter:
          prefix = str(await get_pre(ctx))
          embed = discord.Embed(title= commands[i][0] + " command :", colour=discord.Colour(0x635f), description=commands[i][1])
          embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
          embed.set_author(name="KannaSucre help,")
          embed.add_field(name="User's perms :      ", value="`" + commands[i][3] + "`", inline = True)
          embed.add_field(name="Kanna's perms :      ", value="`" + commands[i][4] + "`", inline = True)
          if commands[i][5] is not None:
            answer = 'no'
            if int(commands[i][5]) == 1:
              answer = 'yes'
            embed.add_field(name="Does the bot need more perms than target to run that command?", value= "```" + answer + "```", inline = False)
          embed.add_field(name="Example : ", value= "```" + prefix + commands[i][2] + "```", inline = False)
          await ctx.send(embed=embed)
          successful = True
      if successful == False :
        await ctx.send("No command named `" + parameter +"` found.")
