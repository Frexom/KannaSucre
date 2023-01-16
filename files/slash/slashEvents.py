from bot import *

from traceback import format_exc


@bot.tree.error
async def on_app_command_error(interaction : discord.Interaction, error: discord.app_commands.AppCommandError):

    if(isinstance(error, discord.app_commands.errors.CommandInvokeError)):
        error = error.original

    if (isinstance(error, discord.Forbidden)):
        content = bot.translator.getLocalString(interaction, "kannaMissPerms", [])
        await interaction.response.send_message(content = content)

    #Error report
    else:
        me = await bot.fetch_user(os.environ['OWNER_ID'])
        message = format_exc()
        if len(message) >= 2000:
            message = message.splitlines()
            middle = int(len(message)/2)

            await me.send('\n'.join(message[:middle]))
            await me.send('\n'.join(message[middle:]))
        else:
            await me.send(message)

        content = bot.translator.getLocalString(interaction, "kannaError", [])
        try:
            await interaction.response.send_message(content = content);
        except Exception as e:
            try:
                await interaction.followup.send(content = content, view = None, embed = None)
            except Exception:
                return
    return


@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command):
    if (not interaction.user.bot):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("INSERT INTO com_history (com_name, user_id, date) VALUES (?,?,?)", (command.name, interaction.user.id , time.time() ))


        #Levels
        if(interaction.guild is not None):
            await cursor.execute("SELECT guild_levels_enabled FROM dis_guild WHERE guild_id = ?", (interaction.guild.id, ))
            enabled = await cursor.fetchone()
        else:
            enabled = [1]
        if enabled[0] == 1:
            await cursor.execute("SELECT user_xp, user_level FROM dis_user WHERE user_id = ?", (interaction.user.id, ))
            user_leveling = await cursor.fetchone()
            user_xp = user_leveling[0]
            user_level = user_leveling[1]
            user_xp += random.randint(90,150)
            if user_xp > 500*user_level:
                user_xp -= 500*user_level
                user_level +=1
                await cursor.execute("UPDATE dis_user SET user_xp = ?, user_level = ? WHERE user_id = ?", (user_xp, user_level, interaction.user.id))
                content = bot.translator.getLocalString(interaction, "levelUp", [("user", interaction.user.mention), ("number", str(user_level))])
                await interaction.channel.send(content = content)
            else:
                await cursor.execute("UPDATE dis_user SET user_xp = ? WHERE user_id = ?", (user_xp, interaction.user.id))


        await connection.commit()
        await close_conn(connection, cursor)
