from connection import *
from prefix import *
from bot import *

sys.path.append("../ressources")

class slashOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name = "preview", description="Makes the bot repeat what you just said.")
    @app_commands.describe(message = "The message to repeat.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def preview(self, interaction : discord.Interaction, message: str):
        if await bot.is_owner(interaction.user):
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("You don't have the permission to use that.")


    @app_commands.command(name="sql", description = "Runs SQL queries, be careful!")
    @app_commands.describe(query = "The query to run.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def sql(self, interaction : discord.Interaction, query : str):
        if await bot.is_owner(interaction.user):
            connection, cursor = await get_conn("./files/ressources/bot.db")
            if(query[0].lower() == "s"):
                await cursor.execute(query)
                result = await cursor.fetchall()
                await close_conn(connection, cursor)
                if result == None:
                    await interaction.response.send_message("None")
                else:
                    await interaction.response.send_message(query + "\n" + str(result), ephemeral = True)
            else:

                await cursor.execute(query)

                sqlInteraction = interaction
                view = discord.ui.View()

                async def commitCallback(interaction):
                    nonlocal connection, cursor, sqlInteraction
                    if interaction.user == sqlInteraction.user:
                        await connection.commit()
                        await sqlInteraction.edit_original_response(content = "Commited.", view = None)
                        await close_conn(connection, cursor)
                commitButton = discord.ui.Button(label = "Commit", style = discord.ButtonStyle.danger, emoji = "⛔")
                commitButton.callback = commitCallback

                async def rollbackCallback(interaction):
                    if interaction.user == sqlInteraction.user:
                        await connection.rollback()
                        await sqlInteraction.edit_original_response(content = "Rolled-back.", view = None)
                        await close_conn(connection, cursor)
                rollbackButton = discord.ui.Button(label = "Rollback", style = discord.ButtonStyle.primary, emoji = "🔙")
                rollbackButton.callback = rollbackCallback

                view.add_item(commitButton)
                view.add_item(rollbackButton)

                await interaction.response.send_message( query + "\n" + str(cursor.rowcount) + " rows affected, do you want to commit?", view = view, ephemeral=True)
        else:
            await interaction.response.send_message("You don't have the permission to use that.")


    @app_commands.command(name="database", description = "Sends the bot's database to the current channel, BE CAREFUL.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def database(self, interaction: discord.Interaction):
        if await bot.is_owner(interaction.user):
            await interaction.response.defer()
            await interaction.followup.send(file=discord.File('files/ressources/bot.db'))
        else:
            await interaction.response.send_message("You don't have the permission to use that.")



    @app_commands.command(name = "shutdown", description = "Shuts down the bot, BE CAREFUL.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def shutdown(self, interaction: discord.Interaction):
        if await bot.is_owner(interaction.user):

            shutdownInteraction = interaction
            view = discord.ui.View()

            async def shutCallback(interaction):
                nonlocal shutdownInteraction
                if interaction.user == shutdownInteraction.user:
                    await shutdownInteraction.edit_original_response(content = "Shutting down...", view = None)
                    await bot.close()
            shutButton = discord.ui.Button(label = "Shutdown", style = discord.ButtonStyle.danger, emoji = "⛔")
            shutButton.callback = shutCallback

            async def cancelCallback(interaction):
                if interaction.user == shutdownInteraction.user:
                    await shutdownInteraction.edit_original_response(content = "Shutdown cancelled.", view = None)
            cancelButton = discord.ui.Button(label = "Cancel", style = discord.ButtonStyle.primary, emoji = "❌")
            cancelButton.callback = cancelCallback

            view.add_item(shutButton)
            view.add_item(cancelButton)

            await interaction.response.send_message("Do you really want to shut down the bot?", view= view)
        else:
            await interaction.response.send_message("You don't have the permission to use that.")

    @app_commands.command(name="sync", description="Sync the bot's commands.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def sync(self, interaction : discord.Interaction):
        if await bot.is_owner(interaction.user):
            await interaction.response.defer()
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
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message("You don't have the permission to use that.")


    @app_commands.command(name="guildcount", description="Shows how many guilds the bot is in.")
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def guildCount(self, interaction: discord.Interaction):
        if await bot.is_owner(interaction.user):
            guilds = len(bot.guilds)
            content = "KannaSucre is in {} guilds., {} more to be verified!".format(guilds, 75-guilds)
            await interaction.response.send_message(content = content)
        else:
            await interaction.response.send_message("You don't have the permission to use that.")



    @app_commands.command(name="status", description="Changes the status of the bot!")
    @app_commands.describe(activity="The new status!")
    @app_commands.choices(status=[
        app_commands.Choice(name="Online", value="online")
        ,app_commands.Choice(name="DoNotDisturb", value="dnd")
        ,app_commands.Choice(name="Idle", value="idle")
        ])
    @app_commands.guilds(int(os.environ['TESTGUILDID']))
    async def status(self, interaction: discord.Interaction,status: app_commands.Choice[str] = "online", activity:str = "Now with Slash commands!", ):
        if await bot.is_owner(interaction.user):
            activity = discord.Game(activity)
            await bot.change_presence(status=status.value, activity=activity)
            await interaction.response.send_message(content = f"Changed status to `{activity}`!")
        else:
            await interaction.response.send_message("You don't have the permission to use that.")
