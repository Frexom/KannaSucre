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
            if(interaction.guild.icon is None):
                content = bot.translator.getLocalString(interaction, "servericon", [])
                await interaction.response.send_message(content = content)
            else:
                await interaction.response.send_message(content = interaction.guild.icon.url)


    @app_commands.command(name = "usericon", description = "Shows an user's avatar!")
    @app_commands.describe(member = "The user you want to see the avatar of!")
    async def usericon(self, interaction: discord.Interaction, member:discord.Member = None):
        if not interaction.user.bot :
            if member == None:
                member = interaction.user
            content = bot.translator.getLocalString(interaction, "usericon", [])
            await interaction.response.send_message(member.display_avatar.url or content)

    @app_commands.command(name="help", description="Get some help about the commands!")
    @app_commands.describe(command="Name of the command you want the details of!")
    async def help(self, interaction = discord.Interaction, command: str = None):
        if not interaction.user.bot :
            connection, cursor = await get_conn("./files/ressources/bot.db")
            if command == None:
                categories = ["__Admin commands :__ \n\n", "\n\n__Moderation commands :__ \n\n", "\n\n__Utilities commands :__ \n\n", "\n\n__Miscellaneous/Fun commands :__ \n\n"]
                await cursor.execute("SELECT com_name, com_short, cat_category FROM com_command ORDER BY cat_category, com_name")
                commands = await cursor.fetchall()
                await close_conn(connection, cursor)
                content = ""
                index = 0
                for i in range(4):
                    content += categories[i]
                    while(index < len(commands) and commands[index][2] == i+1):
                        content += "`" + commands[index][0] +    "` : " + commands[index][1] +"\n"
                        index += 1;
                embed = discord.Embed(title= "Kannasucre help : ", colour=discord.Colour(0x635f))
                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
                embed.add_field(name="** **", value=content)
                await interaction.response.send_message(embed=embed)
            else:
                await cursor.execute("SELECT com_name, com_desc, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM com_command")
                commands = await cursor.fetchall()
                await close_conn(connection, cursor)
                successful = False
                for i in range(len(commands)):
                    if commands[i][0] == command:
                        prefix = "/"
                        embed = discord.Embed(title= commands[i][0] + " command :", colour=discord.Colour(0x635f), description=commands[i][1])
                        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ylO6nSOkZFjyT7oeHcgk6JMQLoxbz727MdJQ9tSUbOs/%3Fsize%3D256/https/cdn.discordapp.com/avatars/765255086581612575/25a75fea0a68fb814d8eada27fc7111e.png")
                        embed.set_author(name="KannaSucre help,")
                        embed.add_field(name="User's perms :            ", value="`" + commands[i][3] + "`", inline = True)
                        embed.add_field(name="Kanna's perms :            ", value="`" + commands[i][4] + "`", inline = True)
                        if commands[i][5] is not None:
                            answer = 'no'
                            if int(commands[i][5]) == 1:
                                answer = 'yes'
                            embed.add_field(name="Does the bot need more perms than target to run that command?", value= "```" + answer + "```", inline = False)
                        embed.add_field(name="Example : ", value= "```" + prefix + commands[i][2] + "```", inline = False)
                        await interaction.response.send_message(embed=embed)
                        successful = True
                if successful == False :
                    await interaction.response.send_message("No command named `" + parameter +"` found.")


    @app_commands.command(name="supportserver", description="Get an invite to KannaSucre's support server!")
    async def supportServer(self, interaction: discord.Interaction):
        if not interaction.user.bot:
            link = os.environ['SUPPORTSERVERLINK']
            t = Translator(interaction.guild.id, loadStrings=True)
            content = bot.translator.getLocalString(interaction, "supportServer", [])
            await interaction.response.send_message(content + link)
