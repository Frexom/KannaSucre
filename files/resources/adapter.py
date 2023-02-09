from typing import Union,Optional
import discord

class ContextAdapter():
    def __init__(self, interaction:Union[discord.Interaction, discord.ext.commands.Context]):
        if(isinstance(interaction, discord.Interaction)):
            self.interaction = interaction
            self.context = None
        if(isinstance(interaction, discord.ext.commands.Context)):
            self.interaction = None
            self.context = interaction
        if(isinstance(interaction, ContextAdapter)):
            self = interaction

        self.message = None




    def getAuthor(self) -> Union[discord.User, discord.Member] :
        if(self.interaction is not None):
            return self.interaction.user
        else:
            return self.context.author


    def getContent(self) -> str:
        if(self.interaction is not None):
            return ""
        else:
            return self.context.message.content


    def getGuild(self) -> discord.Guild:
        if(self.interaction is not None):
            return self.interaction.guild
        else:
            return self.context.guild


    def getChannel(self) -> Optional[Union[discord.abc.GuildChannel, discord.PartialMessageable, discord.Thread]]:
        if(self.interaction is not None):
            return self.interaction.channel
        else:
            return self.context.channel


    def getCommand(self) -> str:
        if(self.interaction is not None):
            return self.interaction.command.name
        else:
            return self.context.command.name

    def getMessage(self) -> discord.Message:
        if(self.interaction is not None):
            return self.interaction.message
        else:
            return self.context.message


    def getClientUser(self) -> discord.ClientUser:
        if(self.interaction is not None):
            return self.interaction.client.user
        else:
            return self.context.me

    def getClient(self) -> discord.Client:
        if(self.interaction is not None):
            return self.interaction.client
        else:
            return self.context.bot


    def isContext(self):
        return self.context is not None


    async def sendMessage(self, **kwargs):
        if(self.interaction is not None):
            if(self.interaction.response.is_done()):
                return await self.followupSend(**kwargs)
            else:
                return await self.interaction.response.send_message(**kwargs)
        else:
            self.message = await self.context.send(**kwargs)
            return self.message


    async def defer(self):
        if(self.interaction is not None and not self.interaction.response.is_done()):
            await self.interaction.response.defer()


    async def followupSend(self, **kwargs):
        if(self.interaction is not None):
            await self.interaction.followup.send(**kwargs)
        else:
            return await self.sendMessage(**kwargs)


    async def editMessage(self, **kwargs):
        if(self.interaction is not None):
            await self.interaction.message.edit(**kwargs)
        elif(self.message != None):
            await self.message.edit(**kwargs)
        else:
            raise ValueError("Message was not set before editing!")


    async def editOriginal(self, **kwargs):
        if(self.interaction is not None):
            await self.interaction.edit_original_response(**kwargs)
        else:
            await self.editMessage(**kwargs)
