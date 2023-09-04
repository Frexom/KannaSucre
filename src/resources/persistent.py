import datetime
import time

import discord
from discord.ext import commands

from src.resources.adapter import ContextAdapter
from src.resources.locales import Translator
from src.resources.prefix import Prefix


class PersistentBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix=Prefix.get_prefix, intents=intents)
        self.remove_command("help")

        self.translator = Translator()

    async def setup_hook(self) -> None:
        self.add_view(GiveawayView(self.translator))


class GiveawayView(discord.ui.View):
    def __init__(self, translator: Translator = None, interaction: discord.Interaction = None):
        super().__init__(timeout=None)

        if translator is not None:
            self.t = translator

        if interaction is not None:
            self.register.label = self.t.getLocalString(interaction, "giveawayRegister", [])

    @discord.ui.button(label="tmp", custom_id="register")
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction = ContextAdapter(interaction)
        if self.t is not None:
            cursor = await interaction.getClient().connection.cursor()
            await cursor.execute(
                "SELECT giv_role_id FROM giv_giveaway WHERE giv_message_id = ? and giv_end_date > ?",
                (interaction.getMessage().id, time.time()),
            )
            reqRole = await cursor.fetchone()

            # If a giveaway has been found
            if reqRole is not None:
                reqRole = reqRole[0]
                isValid = False
                for role in interaction.getAuthor().roles:
                    if reqRole == 0 or role.id == reqRole:
                        isValid = True
                        break

                if isValid:
                    try:
                        await cursor.execute(
                            "INSERT INTO giv_entry (giv_message_id, user_id) VALUES (?,?)",
                            (interaction.getMessage().id, interaction.getAuthor().id),
                        )
                        await interaction.getClient().connection.commit()
                    except sqlite3.IntegrityError:
                        content = self.t.getLocalString(
                            interaction, "giveawayAlreadyRegistered", []
                        )
                        await interaction.sendMessage(content=content, ephemeral=True)
                        return
                    content = self.t.getLocalString(interaction, "giveawayRegistered", [])
                    await interaction.sendMessage(content=content, ephemeral=True)
                else:
                    content = self.t.getLocalString(interaction, "giveawayMissRole", [])
                    await interaction.sendMessage(content=content, ephemeral=True)
            else:
                content = self.t.getLocalString(interaction, "giveawayEnded", [])
                await interaction.sendMessage(content=content, ephemeral=True)

            await cursor.close()


class GiveawayEmbed(discord.Embed):
    def __init__(
        self,
        interaction: discord.Interaction,
        duration: int,
        prize: str,
        role: discord.Role,
        translator: Translator,
    ):
        # Create DatAtime object before changing duration
        ending = datetime.datetime.fromtimestamp(duration + time.time())

        title = translator.getLocalString(interaction, "giveawayStarted", [])

        description = translator.getLocalString(interaction, "giveawayDuration", [])
        if duration > 60 * 60 * 24:
            description += translator.getLocalString(
                interaction, "giveawayDays", [("days", str(duration // 86400))]
            )
            duration = duration % 86400
        if duration > 60 * 60:
            description += translator.getLocalString(
                interaction, "giveawayHours", [("hours", str(duration // 3600))]
            )
            duration = duration % 3600
        if duration >= 60:
            description += translator.getLocalString(
                interaction, "giveawayMinutes", [("minutes", str(duration // 60))]
            )

        super().__init__(title=title, description=description)

        ending = datetime.datetime.fromtimestamp(duration + time.time())
        name = translator.getLocalString(interaction, "giveawayEnds", [])
        self.add_field(name=name, value=ending.strftime("%d/%m/%Y %H:%M") + " UTC+1", inline=True)

        value = (
            translator.getLocalString(interaction, "giveawayNone", [])
            if role is None or role.name == "@everyone"
            else role.mention
        )
        name = translator.getLocalString(interaction, "giveawayRole", [])
        self.add_field(name=name, value=value)

        name = translator.getLocalString(interaction, "giveawayPrize", [])
        self.add_field(name=name, value=f"`{prize}`", inline=False)

        if interaction.getGuild().icon is not None:
            self.set_thumbnail(url=interaction.getGuild().icon.url)
        else:
            self.set_thumbnail(url=interaction.getClientUser().avatar.url)
