from connection import *
from prefix import *
from bot import *

sys.path.append("../resources")

async def previewFunction(interaction : ContextAdapter, message: str):
    if await bot.is_owner(interaction.getAuthor()):
        await interaction.sendMessage(content=message)
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")


async def sqlFunction(interaction : ContextAdapter, query : str):
    if await bot.is_owner(interaction.getAuthor()):
        connection, cursor = await getReadingConn("files/resources/database/bot.db")
        if(query[0].lower() == "s"):
            await cursor.execute(query)
            result = await cursor.fetchall()
            await closeConn(connection, cursor)
            if result == None:
                await interaction.sendMessage(content="None")
            else:
                await interaction.sendMessage(content=query + "\n" + str(result), ephemeral = True)
        else:

            #Only getting rowcount, not comitting on this connection
            await cursor.execute(query)
            rowcount = cursor.rowcount
            await connection.rollback()
            await closeConn(connection, cursor)

            sqlInteraction = interaction
            view = discord.ui.View()

            async def commitCallback(interaction):
                nonlocal sqlInteraction, query
                interaction = ContextAdapter(interaction)

                cursor = await bot.connection.cursor()
                await cursor.execute(query)
                await bot.connection.commit()
                await cursor.close()
                await sqlInteraction.editOriginal(content = "Commited.", view = None)

            commitButton = discord.ui.Button(label = "Commit", style = discord.ButtonStyle.danger, emoji = "⛔")
            commitButton.callback = commitCallback

            async def rollbackCallback(interaction):
                nonlocal sqlInteraction
                await sqlInteraction.editOriginal(content = "Rolled-back.", view = None)

            rollbackButton = discord.ui.Button(label = "Rollback", style = discord.ButtonStyle.primary, emoji = "🔙")
            rollbackButton.callback = rollbackCallback

            view.add_item(commitButton)
            view.add_item(rollbackButton)

            await interaction.sendMessage(content=query + "\n" + str(rowcount) + " rows affected, do you want to commit?", view = view, ephemeral=True)
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")


async def databaseFunction(interaction: ContextAdapter):
    if await bot.is_owner(interaction.getAuthor()):
        await interaction.defer()
        await interaction.followupSend(file=discord.File('files/resources/database/bot.db'))
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")



async def shutdownFunction(interaction: ContextAdapter):
    if await bot.is_owner(interaction.getAuthor()):

        shutdownInteraction = interaction
        view = discord.ui.View()

        async def shutCallback(interaction):
            nonlocal shutdownInteraction
            interaction = ContextAdapter(interaction)
            if interaction.getAuthor() == shutdownInteraction.getAuthor():
                await shutdownInteraction.editOriginal(content = "Shutting down...", view = None)
                await bot.close()
        shutButton = discord.ui.Button(label = "Shutdown", style = discord.ButtonStyle.danger, emoji = "⛔")
        shutButton.callback = shutCallback

        async def cancelCallback(interaction):
            interaction = ContextAdapter(interaction)
            if interaction.getAuthor() == shutdownInteraction.getAuthor():
                await shutdownInteraction.editOriginal(content = "Shutdown cancelled.", view = None)
        cancelButton = discord.ui.Button(label = "Cancel", style = discord.ButtonStyle.primary, emoji = "❌")
        cancelButton.callback = cancelCallback

        view.add_item(shutButton)
        view.add_item(cancelButton)

        await interaction.sendMessage(content="Do you really want to shut down the bot?", view= view)
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")


async def syncFunction(interaction : ContextAdapter):
    if await bot.is_owner(interaction.getAuthor()):
        await interaction.defer()
        guilds = []
        guilds.append(discord.Object(id=os.environ['TESTGUILDID']))
        synced = await bot.tree.sync()
        message = (f"Synced {len(synced)} commands globally.\n")
        ret = 0
        for guild in guilds:
                try:
                        await bot.tree.sync(guild=guild)
                except discord.HTTPException:
                        pass
                else:
                        ret += 1

        message += (f"Synced the tree to {ret}/{len(guilds)} guilds.")
        await interaction.followupSend(content=message, ephemeral=True)
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")


async def guildcountFunction(interaction: ContextAdapter):
    if await bot.is_owner(interaction.getAuthor()):
        guilds = len(bot.guilds)
        content = "KannaSucre is in {} guilds., {} more to be verified!".format(guilds, 75-guilds)
        await interaction.sendMessage(content = content)
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")



async def statusFunction(interaction: ContextAdapter,status: app_commands.Choice[str] = "online", activity:str = "Now with Slash commands!", ):
    if await bot.is_owner(interaction.getAuthor()):
        activity = discord.Game(activity)
        await bot.change_presence(status=status.value, activity=activity)
        await interaction.sendMessage(content = f"Changed status to `{activity}`!")
    else:
        await interaction.sendMessage(content="You don't have the permission to use that.")


async def reloadFunction(interaction: ContextAdapter):
        path = "files.cogs"
        directory = "files/cogs"

        content = "The following files have been reloaded : \n\n```\n"

        for filename in os.listdir("files/cogs/"):

            if os.path.isfile(f"{directory}/{filename}"):
                await bot.unload_extension(f"{path}.{filename[:-3]}")
                await bot.load_extension(f"{path}.{filename[:-3]}")

                content += f"{filename}\n"

        content += "```"
        await interaction.sendMessage(content=content)
