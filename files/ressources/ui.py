from pokemon import *

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
            options.append(discord.SelectOption(label = label, value = i ))
            i += 1
        placeholder = bot.translator.getLocalString(self.interaction, "chooseEvolution", [])
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

class giveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Register!", custom_id="register")
    async def register(self, interaction:discord.Interaction, button: discord.ui.Button):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT giv_role_id FROM giv_giveaway WHERE giv_message_id = ? and giv_end_date > ?", (interaction.message.id, time.time()))
        reqRole = await cursor.fetchone()

        #If a giveaway has been found
        if(reqRole is not None):
            reqRole = reqRole[0]
            isValid = False
            for role in interaction.user.roles:
                if reqRole == 0 or role.id == reqRole:
                    isValid = True
                    break

            if(isValid):
                try:
                    await cursor.execute("INSERT INTO giv_entry (giv_message_id, user_id) VALUES (?,?)", (interaction.message.id, interaction.user.id))
                    await connection.commit()
                except sqlite3.IntegrityError:
                        content = "You already registered for the giveaway!"
                        await interaction.response.send_message(content = content, ephemeral=True)
                        return 
                content = "You have successfully registered for the giveaway!"
                await interaction.response.send_message(content = content, ephemeral=True)
            else:
                content = "I'm sorry, but you miss the required role to enter this giveaway."
                await interaction.response.send_message(content=content, ephemeral=True)
        else:
            content="This giveaway does not exist, it has probably ended!"
            await interaction.response.send_message(content=content, ephemeral=True)

        await close_conn(connection, cursor)


class GiveawayEmbed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, duration:int, prize:str, role:discord.Role):

        #Create DatAtime object before changing duration
        ending = datetime.datetime.fromtimestamp(duration+time.time())


        title = "A new giveaway has started!"
        description = "Duration : "
        if(duration > 60*60*24):
            description += f"{duration//86400} days "
            duration = duration % 86400
        if(duration > 60*60):
            description += f" {duration//3600} hours"
            duration = duration % 3600
        if(duration >= 60):
            description += f" {duration//60} minutes"


        super().__init__(title = title, description=description)

        ending = datetime.datetime.fromtimestamp(duration+time.time())
        self.add_field(name="Ends on :", value=ending.strftime("%d/%m/%Y %H:%M")+" UTC+1", inline=True)
        value = "None" if role is None or role.name == "@everyone" else role.mention
        self.add_field(name="required role :", value = value)
        self.add_field(name="Prize :", value=f"`{prize}`", inline=False)

        if(interaction.guild.icon is not None):
            self.set_thumbnail(url=interaction.guild.icon.url)
        else:
            self.set_thumbnail(url=interaction.client.user.avatar.url)
