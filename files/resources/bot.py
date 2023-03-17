import datetime
import asyncio
import random
import time
import sys
import os

from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from typing import Union
from sclib import SoundcloudAPI, Track, Playlist

from persistent import *
from locales import *
from adapter import *
from prefix import *

load_dotenv()

bot = PersistentBot()
