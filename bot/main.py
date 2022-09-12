import discord
import aiosqlite3
import os
import random
import sys

sys.path.append("./files/slash")
sys.path.append("./files/prefix")
sys.path.append("./files/ressources")

from discord.ext import commands


from connection import *
from prefix import *
from bot import *

from events import *
from owner import *
from admin import *
from setup import *
from moderation import *
from utilities import *
from image_editing import *
from fun import *
from poke import *

from slashUtilities import *
from slashPoke import *
from slashModeration import *
from slashOwner import *
from slashFun import *
from slashAdmin import *


@bot.event
async def on_ready():


    #Adding cogs
    try:
        await bot.add_cog(slashUtilities(bot))
        await bot.add_cog(slashPoke(bot))
        await bot.add_cog(slashModeration(bot))
        await bot.add_cog(slashOwner(bot))
        await bot.add_cog(slashFun(bot))
        await bot.add_cog(slashAdmin(bot))
    #Cog already loaded (while reconnecting)
    except discord.errors.ClientException:
        pass

    #Downtime database update
    for i in range(len(bot.guilds)):
        await setup_func(bot.guilds[i])

    #Appearance
    game = discord.Game('send "ping" to see prefix')
    await bot.change_presence(status=discord.Status.online, activity=game)
    random.seed(time.time())
    print("Bot is ready")




bot.run(os.environ['TOKEN'])
