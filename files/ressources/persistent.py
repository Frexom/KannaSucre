from discord.ext import commands
import discord

from locales import *
from prefix import *

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
