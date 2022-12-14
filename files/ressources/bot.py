import discord
import asyncio
import random
import time
import sys
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from prefix import *
from locales import *

load_dotenv()

default_intents = discord.Intents.default()
default_intents.members = True
default_intents.messages = True
default_intents.message_content = True
bot = commands.Bot(command_prefix=get_pre, intents=default_intents)
bot.remove_command('help')

bot.translator = Translator()
