from src.resources.bot import *
from src.resources.pokemon import *

"""   General Purpose UI   """


class ClearView(discord.ui.View):
    def __init__(self, interaction: ContextAdapter, **kwargs):
        self.interaction = interaction
        super().__init__(**kwargs)

    async def on_timeout(self):
        await self.interaction.editOriginal(view=None)


class CancelButton(discord.ui.Button):
    def __init__(self, interaction: ContextAdapter, prevView: discord.ui.View):
        label = bot.translator.getLocalString(interaction, "cancel", [])
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger, emoji="⚠️")
        self.interaction = interaction
        self.prevView = prevView

    async def callback(self, interaction: discord.Interaction):
        interaction = ContextAdapter(interaction)
        if not interaction.getAuthor().bot:
            if interaction.getAuthor().guild_permissions.manage_guild:
                await interaction.defer()
                await self.interaction.editOriginal(view=self.prevView)


class RefreshButton(discord.ui.Button):
    def __init__(
        self, editInteraction: discord.Interaction, refreshClass: type, **kwargs
    ):
        label = bot.translator.getLocalString(editInteraction, "refresh", [])
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji="🔄")
        self.editInteraction = editInteraction
        self.refreshClass = refreshClass
        self.kwargs = kwargs

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.editInteraction.editOriginal(embed=self.refreshClass(**self.kwargs))


"""   Pokémon UI   """


class PokeDropdown(discord.ui.Select):
    def __init__(self, interaction, pokemon: Pokemon, buttonView: discord.ui.View):
        self.pokemon = pokemon
        self.buttonView = buttonView
        self.interaction = interaction

        noLabel = ["Normal", "Male", "Female"]
        options = []
        i = 0

        for evo in pokemon.evolutions:

            label = evo[2] if evo[3] in noLabel else evo[3] + " " + evo[2]
            options.append(discord.SelectOption(label=label, value=i))
            i += 1
        placeholder = bot.translator.getLocalString(
            self.interaction, "chooseEvolution", []
        )
        super().__init__(
            placeholder=placeholder, options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.pokemon.evolve(int(self.values[0]))
        await interaction.message.edit(
            content=self.pokemon.shiny_link
            if self.pokemon.shiny
            else self.pokemon.link,
            embed=self.pokemon.get_pokeinfo_embed(),
            view=self.buttonView,
        )


"""   Level Reward UI   """


class LevelListEmbed(discord.Embed):
    def __init__(self, interaction: ContextAdapter):
        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT rew_level, rew_role FROM gld_reward WHERE guild_id = ? ORDER BY rew_level",
            (interaction.getGuild().id,),
        )
        levels = cursor.fetchall()

        if len(levels) == 0:
            description = bot.translator.getLocalString(
                interaction, "editlevelNoReward", []
            )
            self.allowedToDelete = False
        else:
            description = ""
            self.allowedToDelete = True
            for row in levels:
                description += bot.translator.getLocalString(
                    interaction,
                    "editLevelReward",
                    [("level", str(row[0])), ("roleID", str(row[1]))],
                )

        title = bot.translator.getLocalString(
            interaction, "editlevelTitle", [("guild", interaction.getGuild().name)]
        )
        super().__init__(title=title, description=description)

        if interaction.getGuild().icon is not None:
            self.set_thumbnail(url=interaction.getGuild().icon.url)
        else:
            self.set_thumbnail(url=interaction.getClientUser().avatar.url)

        text = bot.translator.getLocalString(interaction, "editlevelFooter", [])
        self.set_footer(text=text)

    def isAllowedToDelete(self):
        return self.allowedToDelete


class LevelListView(ClearView):
    def __init__(self, interaction: ContextAdapter, timeout: int = 300):
        super().__init__(interaction=interaction, timeout=timeout)
        self.deleteLevel.label = bot.translator.getLocalString(
            interaction, "editlevelDeleteLabel", []
        )
        self.interaction = interaction

        self.add_item(
            RefreshButton(
                editInteraction=interaction,
                refreshClass=LevelListEmbed,
                interaction=interaction,
            )
        )

    @discord.ui.button(label="tmp", custom_id="deleteLevel")
    async def deleteLevel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        interaction = ContextAdapter(interaction)
        if not interaction.getAuthor().bot:
            await interaction.defer()
            if interaction.getAuthor().guild_permissions.manage_guild:
                try:
                    await self.interaction.editOriginal(
                        view=(ChooseDeleteLevel(interaction))
                    )
                except ValueError:
                    pass


class ChooseDeleteLevel(ClearView):
    def __init__(self, interaction: ContextAdapter, timeout: int = 90):
        super().__init__(interaction=interaction, timeout=timeout)

        self.interaction = interaction
        self.add_item(DeleteLevelDropdown(interaction))

        view = LevelListView(interaction)
        self.add_item(CancelButton(interaction, view))


class DeleteLevelDropdown(discord.ui.Select):
    def __init__(self, interaction: ContextAdapter):
        self.interaction = interaction

        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT rew_level FROM gld_reward WHERE guild_id = ? ORDER BY rew_level",
            (interaction.getGuild().id,),
        )
        levels = cursor.fetchall()
        options = []

        if levels == []:
            raise ValueError("There are no levels to delete!")

        for row in levels:
            options.append(
                discord.SelectOption(label=f"Level {row[0]}", value=int(row[0]))
            )

        placeholder = bot.translator.getLocalString(
            interaction, "editlevelChooseDelete", []
        )
        super().__init__(
            placeholder=placeholder, options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        interaction = ContextAdapter(interaction)
        if not interaction.getAuthor().bot:
            if interaction.getAuthor().guild_permissions.manage_guild:

                cursor = await interaction.getClient().connection.cursor()
                await cursor.execute(
                    "DELETE FROM gld_reward WHERE guild_id = ? AND rew_level = ?",
                    (interaction.getGuild().id, self.values[0]),
                )
                await interaction.getClient().connection.commit()
                await cursor.close()

                content = bot.translator.getLocalString(
                    interaction, "editlevelDeleted", [("level", str(self.values[0]))]
                )
                await interaction.sendMessage(content=content, ephemeral=True)
                embed = LevelListEmbed(self.interaction)
                view = LevelListView(self.interaction)

                await self.interaction.editOriginal(embed=embed, view=view)
