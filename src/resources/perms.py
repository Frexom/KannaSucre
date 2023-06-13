from src.resources.adapter import ContextAdapter


async def missing_perms(
    bot, interaction: ContextAdapter, command_name: str, perms: str = "Not renseigned"
):
    content = bot.translator.getLocalString(
        interaction,
        "missingPerms",
        [("commandName", command_name), ("permission", perms)],
    )
    await interaction.sendMessage(content=content, ephemeral=True)


async def lack_perms(bot, interaction: ContextAdapter, command_name: str):
    content = bot.translator.getLocalString(
        interaction, "lackPerms", [("commandName", command_name)]
    )
    await interaction.sendMessage(content=content, ephemeral=True)


async def dmUnavailable(interaction: ContextAdapter, command_name: str):
    content = f"The `{command_name}` command is not available in direct messages."
    await interaction.sendMessage(content=content, ephemeral=True)
