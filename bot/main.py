import sys
sys.path.append("./files/ressources")
sys.path.append("./files/prefix")
sys.path.append("./files/slash")

from bot import *

from image_editing import *
from moderation import *
from utilities import *
from events import *
from admin import *
from owner import *
from setup import *
from poke import *
from fun import *

from slashModeration import *
from slashUtilities import *
from slashAdmin import *
from slashOwner import *
from slashPoke import *
from slashFun import *



@bot.event
async def on_ready():

    #Adding cogs
    try:
        await bot.add_cog(slashModeration(bot))
        await bot.add_cog(slashUtilities(bot))
        await bot.add_cog(slashAdmin(bot))
        await bot.add_cog(slashOwner(bot))
        await bot.add_cog(slashPoke(bot))
        await bot.add_cog(slashFun(bot))

    #Cog already loaded (while reconnecting)
    except discord.errors.ClientException:
        pass

    #Downtime database update
    for i in range(len(bot.guilds)):
        await setup_func(bot.guilds[i])

    #Starting webhook Listener
    await webhookManager.run(8082)

    #Appearance
    game = discord.Game('send "ping" to see prefix')
    await bot.change_presence(status=discord.Status.online, activity=game)
    random.seed(time.time())
    print("Bot is ready")




bot.run(os.environ['TOKEN'])
