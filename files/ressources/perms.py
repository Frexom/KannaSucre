from bot import *

async def missing_perms(interaction, command_name: str, perms: str = "Not renseigned"):
    content = bot.translator.getLocalString(interaction, "missingPerms", [("commandName", command_name), ("permission", perms)])
    if(isinstance(interaction, discord.Interaction)):
        await interaction.response.send_message(content = content, ephemeral=True)
    else:
        await interaction.send(content = content)


async def lack_perms(interaction, command_name: str):
    content = bot.translator.getLocalString(interaction, "lackPerms", [("commandName", command_name)])
    if(isinstance(interaction, discord.Interaction)):
        await interaction.response.send_message(content = content, ephemeral=True)
    else:
        await interaction.send(content = content)


async def dmUnavailable(interaction, command_name:str):
    content = f"The `{command_name}` command is not available in direct messages."
    if(isinstance(interaction, discord.Interaction)):
        await interaction.response.send_message(content = content, ephemeral=True)
    else:
        await interaction.send(content = content)
