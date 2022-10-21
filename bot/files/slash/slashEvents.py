from bot import *



@bot.tree.error
async def on_app_command_error(interaction : discord.Interaction, error: discord.app_commands.AppCommandError):

    if(isinstance(error, discord.app_commands.errors.CommandInvokeError)):
        error = error.original

    if (isinstance(error, discord.Forbidden)):
        t = Translator(interaction.guild.id)
        await interaction.response.send_message(content = t.getLocalString("kannaMissPerms", []))

    #Error report
    else:
        me = await bot.fetch_user(os.environ['OWNER_ID'])

        await me.send("Error : \n"+str(error))
        t = Translator(interaction.guild.id, loadStrings=True)
        content = t.getLocalString("kannaError", [])
        try:
            await interaction.response.send_message(content = content);
        except Exception as e:
            try:
                await interaction.followup.send(content = content, view = None, embed = None)
            except Exception:
                return
    return
