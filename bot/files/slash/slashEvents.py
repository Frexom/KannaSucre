from bot import *



@bot.tree.error
async def on_app_command_error(interaction : discord.Interaction, error: discord.app_commands.AppCommandError):

    if(isinstance(error, discord.app_commands.errors.CommandInvokeError)):
        error = error.original

    if (isinstance(error, discord.Forbidden)):
        await interaction.response.send_message(await getLocalString(interaction.guild.id, "strings", "kannaMissPerms", []))

    #Error report
    else:
        me = await bot.fetch_user(os.environ['OWNER_ID'])

        await me.send("Error : \n"+str(error))
        content = await getLocalString(interaction.guild.id, "strings", "kannaError", [])
        try:
            await interaction.response.send_message(content = content);
        except Exception as e:
            try:
                await interaction.followup.send(content = content, view = None, embed = None)
            except Exception:
                return
    return
