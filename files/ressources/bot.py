import datetime
import discord
import asyncio
import random
import time
import sys
import os

from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from typing import Union

from locales import *
from prefix import *
from ui import *

load_dotenv()

class PersistentBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix=get_pre, intents=intents)
        self.remove_command('help')

        self.translator = Translator()


    async def setup_hook(self) -> None:
        self.add_view(giveawayView())

bot = PersistentBot()
