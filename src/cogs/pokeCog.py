import discord
from discord import app_commands
from discord.ext import commands

from src.functions.pokeFunctions import (
    pokedexFunction,
    pokeFunction,
    pokeinfoFunction,
    pokerankFunction,
    rollsFunction,
)
from src.resources.adapter import ContextAdapter
from src.resources.mentions import get_target
from src.resources.pokemon import POKE_COUNT


class PokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poke")
    async def poke(self, context):
        await pokeFunction(self.bot, ContextAdapter(context))

    @app_commands.command(name="poke", description="Catch a random pokémon!")
    async def slashPoke(self, interaction: discord.Interaction):
        await pokeFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="pokeinfo")
    async def pokeinfo(self, context):
        message = context.message.content.split(" ")
        if len(message) > 1:
            pokemon = message[1]
            if not pokemon.isdecimal():
                poke_id = self.bot.translator.getPokeIdByName(context, pokemon.lower())
            else:
                poke_id = int(message[1])

            await pokeinfoFunction(self.bot, ContextAdapter(context), poke_id)
        else:
            await context.send("```" + context.prefix + "pokeinfo Poké-Id/Poké-Name```")

    @app_commands.command(name="pokeinfo", description="Shows a pokemon's details!")
    @app_commands.describe(id="The pokemon's pokedex ID.", name="The pokemon's name.")
    async def slashPokeinfo(
        self, interaction: discord.Interaction, id: int = None, name: str = None
    ):
        await pokeinfoFunction(self.bot, ContextAdapter(interaction), id, name)

    @commands.command(name="rolls")
    async def rolls(self, context):
        await rollsFunction(self.bot, ContextAdapter(context))

    @app_commands.command(
        name="rolls",
        description="Displays how much pokerolls you have, and when your next free roll will be.",
    )
    async def slashRolls(self, interaction: discord.Interaction):
        await rollsFunction(self.bot, ContextAdapter(interaction))

    @commands.command(name="pokedex")
    async def pokedex(self, context):
        if not context.author.bot:
            user = get_target(context)
            if user is not None:
                message = context.message.content.split(" ")
                page = 1
                if len(message) > 1 and message[1].isdecimal():
                    page = int(message[1])

                    outOfRange = page < 1 or page > int(POKE_COUNT / 20) + 1
                    if outOfRange:
                        page = 1

                await pokedexFunction(self.bot, ContextAdapter(context), user, page)
            else:
                await context.send("```" + context.prefix + "pokedex *page number* @user```")

    @app_commands.command(
        name="pokedex",
        description="Shows all the pokemons someone caught in their pokedex.",
    )
    @app_commands.describe(
        user="The user you want to see the pokedex of.",
        page="The pokedex's page you want to see.",
    )
    async def slashPokedex(
        self, interaction: discord.Interaction, user: discord.User = None, page: int = 1
    ):
        await pokedexFunction(self.bot, ContextAdapter(interaction), user, page)

    @commands.command(name="pokerank")
    async def pokerank(self, context):
        await pokerankFunction(self.bot, ContextAdapter(context))

    @app_commands.command(
        name="pokerank", description="Displays the bot's top 10 best pokemon trainers!"
    )
    async def slashPokerank(self, interaction: discord.Interaction):
        await pokerankFunction(self.bot, ContextAdapter(interaction))


async def setup(bot):
    await bot.add_cog(PokeCog(bot))
