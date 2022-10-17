from bot import *

async def missing_perms(ctx, command_name: str, perms: str = "Not renseigned"):
    content = await getLocalString(ctx.guild.id, "strings", "missingPerms", [("commandName", command_name), ("permission", perms)])
    if(isinstance(ctx, discord.Interaction)):
        await ctx.response.send_message(content = content, ephemeral=True)
    else:
        await ctx.send(content = content)


async def lack_perms(ctx, command_name: str):
    content = await getLocalString(ctx.guild.id, "strings", "lackPerms", [("commandName", command_name)])
    if(isinstance(ctx, discord.Interaction)):
        await ctx.response.send_message(content = content, ephemeral=True)
    else:
        await ctx.send(content = content)
