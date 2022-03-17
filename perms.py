async def missing_perms(ctx, command_name: str, perms: str = "Not renseigned"):
  await ctx.send("I'm sorry but you don't meet the requirements to run that command : `" + command_name + "`.\nThis command requires the following permission : `" + perms + "`.")


async def lack_perms(ctx, command_name: str):
  await ctx.send("I'm sorry but the command target has as much as or more permissions than you. You can't target them with the following command : `" + command_name + "`.")
