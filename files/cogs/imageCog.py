from PIL import Image, ImageFont, ImageDraw

from connection import *
from mentions import *
from prefix import *
from bot import *

from imageFunctions import *

class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="level")
    async def level(self, context):
        user = get_target(context)

        await levelFunction(ContextAdapter(context), user)


    @app_commands.command(name="level", description="Displays your level and XP.")
    @app_commands.describe(user="The user you want to see the level of.")
    async def slashLevel(self, interaction: discord.Interaction, user: discord.User = None):
        await levelFunction(ContextAdapter(interaction), user)



async def setup(bot):
    await bot.add_cog(ImageCog(bot))
