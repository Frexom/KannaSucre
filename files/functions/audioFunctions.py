from bot import *

async def soundcloudFunction(interaction:ContextAdapter):
    api = SoundcloudAPI()
    track = api.resolve("https://soundcloud.com/oldishosusongs/will-stetson-honesty-swing-arrangement")
    filename = f"./{track.artist} - {track.title}.mp3"
    with open(filename, 'wb+') as file:
        track.write_mp3_to(file)


    await interaction.sendMessage(content = "done!")

async def playFunction(interaction: ContextAdapter):
    user = interaction.getAuthor()
    voiceChannel = user.voice.channel
    if(voiceChannel != None):
        await interaction.sendMessage(content = "Right now!")

        vc = await voiceChannel.connect()
        voiceClient = interaction.getGuild().voice_client
        voiceClient.play(discord.FFmpegPCMAudio(source="./will stetson - honesty (swing arrangement).mp3"))

        while(voiceClient.is_playing()):
            await asyncio.sleep(1)

        await voiceClient.stop()
        await vc.disconnect()
