import discord

from src.resources.adapter import ContextAdapter


async def diceFunction(interaction: ContextAdapter, max: int = 6):
    if not interaction.getAuthor().bot:
        number = str(random.randint(1, max))
        content = bot.translator.getLocalString(
            interaction, "diceRoll", [("randomNumber", number), ("maxNumber", max)]
        )
        await interaction.sendMessage(content=content)


async def servericonFunction(interaction: ContextAdapter):
    if not interaction.getAuthor().bot:
        if interaction.getGuild() is not None:
            if interaction.getGuild().icon is None:
                content = bot.translator.getLocalString(interaction, "servericon", [])
                await interaction.sendMessage(content=content)
            else:
                await interaction.sendMessage(content=interaction.getGuild().icon.url)
        else:
            await dmUnavailable(interaction, "servericon")


async def usericonFunction(
    interaction: ContextAdapter, member: discord.Member | discord.User = None
):
    if not interaction.getAuthor().bot:
        if member == None:
            member = interaction.getAuthor()
        content = bot.translator.getLocalString(interaction, "usericon", [])
        await interaction.sendMessage(content=member.display_avatar.url or content)


async def supportserverFunction(interaction: ContextAdapter):
    if not interaction.getAuthor().bot:
        link = os.environ["SUPPORTSERVERLINK"]
        content = bot.translator.getLocalString(interaction, "supportServer", [])
        await interaction.sendMessage(content=content + link)


async def dailyFunction(interaction: ContextAdapter):
    if not interaction.getAuthor().bot:

        cursor = await bot.connection.cursor()
        await cursor.execute(
            "SELECT user_balance, user_last_daily_day FROM dis_user WHERE user_id = ?",
            (interaction.getAuthor().id,),
        )
        userWallet = await cursor.fetchone()

        now = time.time()
        daysSince = (now - (now % (24 * 60 * 60))) / (24 * 60 * 60)

        responseMessage = ""
        if daysSince != userWallet[1]:
            await cursor.execute(
                "UPDATE dis_user SET user_balance = user_balance + 100, user_last_daily_day = ? WHERE user_id = ?",
                (
                    daysSince,
                    interaction.getAuthor().id,
                ),
            )
            responseMessage += "100 KannaCoins have been added to your balance!\n"
            responseMessage += (
                f"That makes **{str(userWallet[0]+100)} KannaCoins** on your account."
            )
        else:

            timeLeft = (daysSince * 24 * 60 * 60) + 24 * 60 * 60 - now

            hours = int(timeLeft // (60 * 60))
            minutes = int((timeLeft % (60 * 60)) // 60)
            responseMessage = f"You cannot get your daily coins yet, please wait {hours} hours and {minutes} minutes.\n"

        await interaction.sendMessage(content=responseMessage)
        await cursor.close()


async def servrankFunction(interaction: ContextAdapter):
    if not interaction.getAuthor().bot:

        await interaction.defer()

        cursor = await bot.connection.cursor()
        await cursor.execute(
            "SELECT lev_level, user_name FROM gld_level JOIN dis_user USING(user_id) WHERE guild_id = ? AND lev_level != 0 ORDER BY lev_level DESC, lev_xp DESC limit 10",
            (interaction.getGuild().id,),
        )
        result = await cursor.fetchall()
        await cursor.close()
        result_list = []
        for i in range(len(result)):
            result_list.append([result[i][0], result[i][1]])
        description = ""
        i = 0
        limit = 10
        while i != len(result_list) and i < 10:
            description += str(i + 1) + " - "
            description += bot.translator.getLocalString(
                interaction,
                "servrankLevel",
                [("username", result_list[i][1]), ("level", str(result_list[i][0]))],
            )
            description += "\n"
            i += 1

        if description == "":
            description = bot.translator.getLocalString(interaction, "servrankEmpty", [])

        title = bot.translator.getLocalString(interaction, "pokerank", [])
        embed = discord.Embed(title=title, colour=discord.Colour(0x635F))

        if interaction.getGuild().icon is not None:
            embed.set_thumbnail(url=interaction.getGuild().icon.url)
        else:
            embed.set_thumbnail(url=interaction.getClientUser().avatar.url)

        name = bot.translator.getLocalString(
            interaction, "servrankRanking", [("guild", interaction.getGuild().name)]
        )
        embed.add_field(name=name, value=description)
        await interaction.followupSend(embed=embed)


async def helpFunction(interaction: ContextAdapter, command: str = None):
    if not interaction.getAuthor().bot:
        cursor = await bot.connection.cursor()
        if command == None:

            categories = []
            categories.append(bot.translator.getLocalString(interaction, "helpCatAdmin", []))
            categories.append(bot.translator.getLocalString(interaction, "helpCatMod", []))
            categories.append(bot.translator.getLocalString(interaction, "helpCatUtil", []))
            categories.append(bot.translator.getLocalString(interaction, "helpCatMisc", []))

            await cursor.execute(
                "SELECT com_name, cat_category FROM com_command ORDER BY cat_category, com_name"
            )
            commands = await cursor.fetchall()
            await cursor.close()

            title = bot.translator.getLocalString(interaction, "helpBigTitle", [])
            embed = discord.Embed(title=title, colour=discord.Colour(0x635F))
            embed.set_thumbnail(url=bot.user.avatar.url)
            index = 0
            for i in range(4):
                content = ""
                while index < len(commands) and commands[index][1] == i + 1:
                    comShort = bot.translator.getLocalString(
                        interaction, commands[index][0] + "Short", []
                    )
                    content += "`" + commands[index][0] + "` : " + comShort + "\n"
                    index += 1
                embed.add_field(name=categories[i], value=content, inline=False)
            await interaction.sendMessage(embed=embed)
        else:
            await cursor.execute(
                "SELECT com_name, com_use_example, com_user_perms, com_bot_perms, com_more_perms_than_target FROM com_command"
            )
            commands = await cursor.fetchall()
            await cursor.close()
            successful = False
            for i in range(len(commands)):
                if commands[i][0] == command:
                    prefix = "/"
                    description = bot.translator.getLocalString(
                        interaction, commands[i][0] + "Desc", []
                    )
                    title = bot.translator.getLocalString(
                        interaction, "helpTitle", [("command", commands[i][0])]
                    )
                    embed = discord.Embed(
                        title=title,
                        colour=discord.Colour(0x635F),
                        description=description,
                    )
                    embed.set_thumbnail(url=bot.user.avatar.url)
                    name = bot.translator.getLocalString(interaction, "helpUserPerms", [])
                    embed.add_field(name=name, value="`" + commands[i][2] + "`", inline=True)
                    name = bot.translator.getLocalString(interaction, "helpKannaPerms", [])
                    embed.add_field(
                        name="Kanna's perms :",
                        value="`" + commands[i][3] + "`",
                        inline=True,
                    )
                    if commands[i][4] is not None:
                        answer = bot.translator.getLocalString(interaction, "helpNo", [])
                        if int(commands[i][4]) == 1:
                            answer = bot.translator.getLocalString(interaction, "helpYes", [])
                        name = bot.translator.getLocalString(interaction, "helpMorePerms", [])
                        embed.add_field(name=name, value="```" + answer + "```", inline=False)
                    name = bot.translator.getLocalString(interaction, "helpExample", [])
                    embed.add_field(
                        name=name,
                        value="```" + prefix + commands[i][1] + "```",
                        inline=False,
                    )
                    await interaction.sendMessage(embed=embed)
                    successful = True
            if successful == False:
                content = bot.translator.getLocalString(
                    interaction, "helpNoCommand", [("name", command)]
                )
                await interaction.sendMessage(content=content)
