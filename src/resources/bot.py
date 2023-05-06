from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from src.resources.adapter import *
from src.resources.locales import *
from src.resources.persistent import *
from src.resources.prefix import *

load_dotenv()

bot = PersistentBot()
