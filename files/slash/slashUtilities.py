from perms import *
from bot import *

sys.path.append("../ressources")


class slashUtilities(commands.Cog):
    def __init__(self, bot):
            self.bot = bot

    @app_commands.command(name = "dice", description = "Rolls a dice!")
    @app_commands.describe(max="The largest number included.")
    async def dice(self, interaction: discord.Interaction, max: int = 6):
        if not interaction.user.bot:
            number = str(random.randint(1, max))
            content = bot.translator.getLocalString(interaction, "diceRoll", [("randomNumber", number), ("maxNumber", max)])
            await interaction.response.send_message(content = content)


    @app_commands.command(name = "servericon", description = "Shows the server's icon!")
    async def servericon(self, interaction: discord.Interaction):
        if not interaction.user.bot :
            if(interaction.guild is not None):
                if(interaction.guild.icon is None):
                    content = bot.translator.getLocalString(interaction, "servericon", [])
                    await interaction.response.send_message(content = content)
                else:
                    await interaction.response.send_message(content = interaction.guild.icon.url)
            else:
                await dmUnavailable(interaction, "servericon")


    @app_commands.command(name = "usericon", description = "Shows an user's avatar!")
    @app_commands.describe(member = "The user you want to see the avatar of!")
    async def usericon(self, interaction: discord.Interaction, member: Union[discord.Member, discord.User] = None):
        if not interaction.user.bot :
            if member == None:
                member = interaction.user
            content = bot.translator.getLocalString(interaction, "usericon", [])
            await interaction.response.send_message(member.display_avatar.url or content)


    @app_commands.command(name="supportserver", description="Get an invite to KannaSucre's support server!")
    async def supportServer(self, interaction: discord.Interaction):
        if not interaction.user.bot:
            link = os.environ['SUPPORTSERVERLINK']
            content = bot.translator.getLocalString(interaction, "supportServer", [])
            await interaction.response.send_message(content + link)

    @app_commands.command(name="help", description="Get some help about the commands!")
    @app_commands.describe(command="Name of the command you want the details of!")
    async def help(self, interaction = discord.Interaction, command: str = None):
        if not interaction.user.bot :
            connection, cursor = await get_conn("./files/ressources/bot.db")
            if command == None:

                categories = []
                categories.append(bot.translator.getLocalString(interaction, "helpCatAdmin", []))
                categories.append(bot.translator.getLocalString(interaction, "helpCatMod", []))
                categories.append(bot.translator.getLocalString(interaction, "helpCatUtil", []))
                categories.append(bot.translator.getLocalString(interaction, "helpCatMisc", []))

                await cursor.execute("SELECT com_name, cat_category FROM com_command ORDER BY cat_category, com_name")
                commands = await cursor.fetchall()
                await close_conn(connection, cursor)

                title = bot.translator.getLocalString(interaction, "helpBigTitle", [])
                embed = discord.Embed(title= title, colour=discord.Colour(0x635f))
                embed.set_thumbnail(url=bot.user.avatar.url)
                index = 0
                for i in range(4):
                    content = ""
                    while(index < len(commands) and commands[index][1] == i+1):
                        comShort = bot.translator.getLocalString(interaction, commands[index][0]+"Short", [])
                        content += "`" + commands[index][0] +    "` : " + comShort +"\n"
                        index += 1
                    embed.add_field(name=categories[i], value=content, inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await cursor.execute("SELECT com_name, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM com_command")
                commands = await cursor.fetchall()
                await close_conn(connection, cursor)
                successful = False
                for i in range(len(commands)):
                    if commands[i][0] == command:
                        prefix = "/"
                        description = bot.translator.getLocalString(interaction, commands[i][0]+"Desc", [])
                        title = bot.translator.getLocalString(interaction, "helpTitle", [("command", commands[i][0])])
                        embed = discord.Embed(title= title, colour=discord.Colour(0x635f), description=description)
                        embed.set_thumbnail(url=bot.user.avatar.url)
                        name = bot.translator.getLocalString(interaction, "helpUserPerms", [])
                        embed.add_field(name=name, value="`" + commands[i][2] + "`", inline = True)
                        name = bot.translator.getLocalString(interaction, "helpKannaPerms", [])
                        embed.add_field(name="Kanna's perms :", value="`" + commands[i][3] + "`", inline = True)
                        if commands[i][4] is not None:
                            answer = bot.translator.getLocalString(interaction, "helpNo", [])
                            if int(commands[i][4]) == 1:
                                answer = bot.translator.getLocalString(interaction, "helpYes", [])
                            name = bot.translator.getLocalString(interaction, "helpMorePerms", [])
                            embed.add_field(name=name, value= "```" + answer + "```", inline = False)
                        name = bot.translator.getLocalString(interaction, "helpExample", [])
                        embed.add_field(name=name, value= "```" + prefix + commands[i][1] + "```", inline = False)
                        await interaction.response.send_message(embed=embed)
                        successful = True
                if successful == False :
                    content = bot.translator.getLocalString(interaction, "helpNoCommand", [("name", command)])
                    await interaction.response.send_message(content = content)
