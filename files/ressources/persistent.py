from discord.ext import commands
import discord
import datetime
import time

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
        self.add_view(giveawayView(self.translator))



class giveawayView(discord.ui.View):
    def __init__(self, translator :Translator = None, interaction:discord.Interaction = None):
        super().__init__(timeout = None)

        if(translator is not None):
            self.t = translator

        if(interaction is not None):
            self.register.label = self.t.getLocalString(interaction, "giveawayRegister", [])


    @discord.ui.button(label="tmp", custom_id="register")
    async def register(self, interaction:discord.Interaction, button: discord.ui.Button):
        if(self.t is not None):
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
                        content = self.t.getLocalString(interaction, "giveawayAlreadyRegistered", [])
                        await interaction.response.send_message(content = content, ephemeral=True)
                        return
                    content = self.t.getLocalString(interaction, "giveawayRegistered", [])
                    await interaction.response.send_message(content = content, ephemeral=True)
                else:
                    content = self.t.getLocalString(interaction, "giveawayMissRole", [])
                    await interaction.response.send_message(content=content, ephemeral=True)
            else:
                content = self.t.getLocalString(interaction, "giveawayEnded", [])
                await interaction.response.send_message(content=content, ephemeral=True)

            await close_conn(connection, cursor)


class GiveawayEmbed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, duration:int, prize:str, role:discord.Role, translator:Translator):

        #Create DatAtime object before changing duration
        ending = datetime.datetime.fromtimestamp(duration+time.time())

        title = translator.getLocalString(interaction, "giveawayStarted", [])

        description = translator.getLocalString(interaction, "giveawayDuration", [])
        if(duration > 60*60*24):
            description += translator.getLocalString(interaction, "giveawayDays", [("days", str(duration//86400))])
            duration = duration % 86400
        if(duration > 60*60):
            description += translator.getLocalString(interaction, "giveawayHours", [("hours", str(duration//3600))])
            duration = duration % 3600
        if(duration >= 60):
            description += translator.getLocalString(interaction, "giveawayMinutes", [("minutes", str(duration//60))])


        super().__init__(title = title, description=description)

        ending = datetime.datetime.fromtimestamp(duration+time.time())
        name = translator.getLocalString(interaction, "giveawayEnds", [])
        self.add_field(name=name, value=ending.strftime("%d/%m/%Y %H:%M")+" UTC+1", inline=True)

        value = translator.getLocalString(interaction, "giveawayNone", []) if role is None or role.name == "@everyone" else role.mention
        name=translator.getLocalString(interaction, "giveawayRole", [])
        self.add_field(name=name, value = value)

        name=translator.getLocalString(interaction, "giveawayPrize", [])
        self.add_field(name=name, value=f"`{prize}`", inline=False)

        if(interaction.guild.icon is not None):
            self.set_thumbnail(url=interaction.guild.icon.url)
        else:
            self.set_thumbnail(url=interaction.client.user.avatar.url)