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
