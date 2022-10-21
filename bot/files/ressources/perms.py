from bot import *

async def missing_perms(interaction, command_name: str, perms: str = "Not renseigned"):
    t = Translator(interaction.guild.id, loadStrings = True)
    content = t.getLocalString("missingPerms", [("commandName", command_name), ("permission", perms)])
    if(isinstance(interaction, discord.Interaction)):
        await interaction.response.send_message(content = content, ephemeral=True)
    else:
        await interaction.send(content = content)


async def lack_perms(interaction, command_name: str):
    t = Translator(interaction.guild.id, loadStrings = True)
    content = t.getLocalString("lackPerms", [("commandName", command_name)])
    if(isinstance(interaction, discord.Interaction)):
        await interaction.response.send_message(content = content, ephemeral=True)
    else:
        await interaction.send(content = content)
