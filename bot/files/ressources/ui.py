from pokemon import *
from bot import *

class PokeDropdown(discord.ui.Select):
    def __init__(self, pokemon: Pokemon, buttonView: discord.ui.View):
        self.pokemon = pokemon
        self.buttonView = buttonView

        noLabel = ["Normal", "Male", "Female"]
        options = []
        i = 0

        for evo in pokemon.evolutions:

            label = evo[2] if evo[3] in noLabel else evo[3] + " " + evo[2]
            options.append(discord.SelectOption(label = label, value = i ))
            i += 1

        super().__init__(placeholder = "Choose an evolution", options = options, min_values = 1, max_values = 1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.pokemon.evolve(int(self.values[0]))
        await interaction.message.edit(content = self.pokemon.shiny_link if self.pokemon.shiny else self.pokemon.link, embed = self.pokemon.get_pokeinfo_embed(), view = self.buttonView)
