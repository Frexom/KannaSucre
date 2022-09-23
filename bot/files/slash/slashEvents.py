from bot import *



@bot.tree.error
async def on_app_command_error(interaction : discord.Interaction, error: discord.app_commands.AppCommandError):

    if(isinstance(error, discord.app_commands.errors.CommandInvokeError)):
        error = error.original

    if (isinstance(error, discord.Forbidden)):
        await interaction.response.send_message("I don't have enough permissions to do that!")

    #Error report
    else:
        me = await bot.fetch_user(os.environ['OWNER_ID'])
        await me.send(error)

        try:
            await interaction.response.send_message("There was an error, it will be reported to staff.");
        except Exception as e:
            try:
                await interaction.followup.send("There was an error, it will be reported to staff.", view = None, embed = None)
            except Exception:
                return
    return
