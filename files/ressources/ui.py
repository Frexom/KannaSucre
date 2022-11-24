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
        placeholder = self.pokemon.translator.getLocalString("chooseEvolution", [])
        super().__init__(placeholder = placeholder, options = options, min_values = 1, max_values = 1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.pokemon.evolve(int(self.values[0]))
        await interaction.message.edit(content = self.pokemon.shiny_link if self.pokemon.shiny else self.pokemon.link, embed = self.pokemon.get_pokeinfo_embed(), view = self.buttonView)


class pokeView(discord.ui.View):
    def __init__(self, timeout:int = 90):
        super().__init__(timeout = timeout)
        self.message = None

    def setMessage(self, message: discord.Message):
        self.message = message;

    async def on_timeout(self):
        if(self.message is not None):
            if(isinstance(self.message, discord.Interaction)):
                await self.message.edit_original_response(view=None)
            elif(isinstance(self.message, discord.Message)):
                await self.message.edit(view = None)
            else:
                raise AttributeError("Timeout message was improperly set.")
        else:
            raise AttributeError("Timeout message was not set.")
