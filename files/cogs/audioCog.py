from bot import *

from audioFunctions import *

class AudioCog(commands.Cog):
    def __init__(self, bot):
            self.bot = bot


    @commands.command(name="soundcloud")
    @commands.is_owner()
    async def soundcloud(self, context):
        await soundcloudFunction(ContextAdapter(context))

    @commands.command(name="play")
    @commands.is_owner()
    async def play(self, context):
        await playFunction(ContextAdapter(context))


async def setup(bot):
    await bot.add_cog(AudioCog(bot))
