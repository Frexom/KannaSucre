import os
import random
import time

import aiosqlite3
import discord
from discord.ext import tasks

from src.functions.eventsFunctions import setup_func
from src.resources.bot import bot


@bot.event
async def on_ready():
    bot.connection = await aiosqlite3.connect("src/resources/database/bot.db")

    # Adding cogs
    path = "src.cogs"
    for filename in os.listdir("src/cogs/"):
        if os.path.isfile(f"src/cogs/{filename}"):
            try:
                await bot.load_extension(f"{path}.{filename[:-3]}")
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                print(f"{path}.{filename[:-3]} : Cog already loaded")

    try:
        await bot.load_extension("src.functions.eventsFunctions")
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        print(f"src.functions.eventsFunctions : Cog already loaded")

    # Downtime database update
    for i in range(len(bot.guilds)):
        await setup_func(bot, bot.guilds[i])

    # Appearance
    game = discord.Game("Now with slash commands!")
    await bot.change_presence(status=discord.Status.online, activity=game)
    random.seed(time.time())
    try:
        checkEndedGiveaways.start()
    except RuntimeError:
        pass
    print("Bot is ready")


@tasks.loop(seconds=30)
async def checkEndedGiveaways():
    cursor = await bot.connection.cursor()
    await cursor.execute(
        """
    SELECT giv_message_id, giv_channel_id, giv_prize,
    (
        SELECT user_id FROM giv_entry WHERE giv_giveaway.giv_message_id = giv_message_id ORDER BY RANDOM() LIMIT 1
    ) as giv_winner,
	(
        SELECT COUNT(*) FROM giv_entry WHERE giv_giveaway.giv_message_id = giv_message_id
    ) as giv_count
    FROM giv_giveaway WHERE giv_ended = 0 and giv_end_date < STRFTIME('%s')
    """
    )
    giveaways = await cursor.fetchall()

    for giveaway in giveaways:
        channel = bot.get_channel(giveaway[1])
        message = await channel.fetch_message(giveaway[0])

        if giveaway[3] is None:
            content = bot.translator.getLocalString(channel, "giveawayLost", [])
        else:
            content = bot.translator.getLocalString(
                channel,
                "giveawayWon",
                [
                    ("number", str(giveaway[4])),
                    ("userId", str(giveaway[3])),
                    ("prize", str(giveaway[2])),
                ],
            )
        await channel.send(content=content, reference=message)
        await cursor.execute(
            "UPDATE giv_giveaway SET giv_ended = 1 WHERE giv_message_id = ?",
            (giveaway[0],),
        )
        await bot.connection.commit()

    await cursor.close()


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    interaction = ContextAdapter(interaction)

    if isinstance(error, discord.app_commands.errors.CommandInvokeError):
        error = error.original

    if isinstance(error, discord.Forbidden):
        content = bot.translator.getLocalString(interaction, "kannaMissPerms", [])
        await interaction.sendMessage(content=content)

    # Error report
    else:
        me = await bot.fetch_user(os.environ["OWNER_ID"])
        message = format_exc()
        if len(message) >= 2000:
            message = message.splitlines()
            middle = int(len(message) / 2)

            await me.send("\n".join(message[:middle]))
            await me.send("\n".join(message[middle:]))
        else:
            await me.send(message)

        content = bot.translator.getLocalString(interaction, "kannaError", [])
        try:
            await interaction.sendMessage(content=content)
        except Exception as e:
            try:
                await interaction.followupSend(content=content, view=None, embed=None)
            except Exception:
                return
    return


bot.run(os.environ["TOKEN"])
