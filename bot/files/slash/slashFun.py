from connection import *
from prefix import *
from bot import *

sys.path.append("../ressources")

class slashFun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "hug", description = "Lets you hug someone!")
    @app_commands.describe(user = "The user you want to hug!")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
      if not interaction.user.bot :
          hugList = [
                "https://media1.tenor.com/images/89272929c73eefcca4b5f0ec8fe30316/tenor.gif",
                "https://media1.tenor.com/images/1f44c379b43bc4efb6d227a2e20b6b50/tenor.gif",
                "https://images-ext-1.discordapp.net/external/z1Qpvvs0jTvOCec0o_DCD7sU78QC3iT36SnX9EgOPEY/%3Fitemid%3D17730757/https/media1.tenor.com/images/3be3bf592e86d05c89367054a41ff827/tenor.gif",
                "https://images-ext-1.discordapp.net/external/eysfKhUmPR2mbZvLeztQApTxHuKYK69wN-J_wNqQd4s/%3Fitemid%3D15793132https%3A%2F%2Fmedia1.tenor.com%2Fimages%2F7fd514d641f597ac0748c04e47a88d2e%2Ftenor.gif%3Fitemid%3D15793132/https/media1.tenor.com/images/7fd514d641f597ac0748c04e47a88d2e/tenor.gif",
                "https://images-ext-1.discordapp.net/external/xZBEqIadMz71rwKo8VjOCLM9U2qoa5ecw9_T-K7_QdA/%3Fitemid%3D5950582/https/media1.tenor.com/images/96ba07b09e81f9cec49e14a18ba6f701/tenor.gif",
                "https://images-ext-2.discordapp.net/external/cCaEjMcviogmY3aIM0Tt1O_pt4FIRKGA2RrONd-bkww/%3Fitemid%3D14837114/https/media1.tenor.com/images/53916bb4116361f65f9649fd73f366b1/tenor.gif",
                "https://media1.tenor.com/images/f77f9b5c2b20592135431e8a1d536d25/tenor.gif",
                "https://images-ext-2.discordapp.net/external/D8HwdbQ9gjBS5YJnILN8eHXnI1RjfdCMvrcu875ALcU/%3Fitemid%3D17731947/https/media1.tenor.com/images/8727180629ffd5b91ae5674ab264b98f/tenor.gif",
                "https://images-ext-2.discordapp.net/external/tRosj_eohSEf6jbPTcAp0RTY9DfFwpg3tmNogHevFy0/%3Fitemid%3D5680708/https/media1.tenor.com/images/65913379d468b61cd6eb6337c394dccb/tenor.gif",
                "https://images-ext-1.discordapp.net/external/TDmTVkLYuUF2JHH1MTVVUmy8K8EqBoREL2zFJJCt4jA/%3Fitemid%3D13883173/https/media1.tenor.com/images/3c7a770da649c31628f60696962cefca/tenor.gif",
                "https://images-ext-2.discordapp.net/external/AcyEgRazC8yGg71BDrSNvve4qL6nQNp9DHYnP3d--Fw/%3Fitemid%3D9469908/https/media1.tenor.com/images/567fa5edc9aa36dc8b8b00e02b25a352/tenor.gif",
                "https://images-ext-2.discordapp.net/external/PeE1dkLkpyFP18LAXukZCgVoyIHRkOEsKUqzizwWum0/%3Fitemid%3D17584778/https/media1.tenor.com/images/6398ebd19b8f7907a6a16b63e78de7a5/tenor.gif",
                "https://images-ext-1.discordapp.net/external/KJCVyu02jhCZtxuRKIqBH4d3bUWFruRrkCi6DOT1WvI/%3Fitemid%3D14916283/https/media1.tenor.com/images/c715ff7b4fcb2edabd198cedd14d1016/tenor.gif",
                "https://images-ext-1.discordapp.net/external/l61p6wTavtc8jdJsd06_201UeroKhf0C8u8KwdK00DM/%3Fitemid%3D5324255/https/media1.tenor.com/images/c00119443474a031024af2e299947cb8/tenor.gif",
                "https://images-ext-1.discordapp.net/external/ZojPlwyvQiqBkW4ZcuRjwXNzxihEjhohTJ0gl_jMX44/%3Fitemid%3D7992213/https/media1.tenor.com/images/35e8def510afb07b2f7813f6db2047da/tenor.gif",
                "https://images-ext-2.discordapp.net/external/TMoEi3-QXGVFhij85MbmpSevHYcmJ9MVC3iI9Sd2Bpw/%3Fitemid%3D4944125/https/media1.tenor.com/images/159577058f86a9cf6faeed7e3141f5bc/tenor.gif",
                "https://images-ext-2.discordapp.net/external/dzPVkmC21Trw5fHHLZkQtjD0-V5DXdO-66JC-NFnM28/%3Fitemid%3D16843221/https/media1.tenor.com/images/75f007f2541a2d8581b2558af7190714/tenor.gif",
                "https://images-ext-2.discordapp.net/external/n04k5Cp3E1va5CfBtK6yVw4-8MoZQT1UWyXNTufkapE/%3Fitemid%3D17622299/https/media1.tenor.com/images/e960bd971a80f2d97aff1aa16df84663/tenor.gif",
                "https://images-ext-1.discordapp.net/external/wrPKqJpZ8zA1lvRVRBReA9eXjW1wXrdVbxYEw0bTqHQ/%3Fitemid%3D15575523/https/media1.tenor.com/images/e57ae19196e9ce618e21e0fd87985afc/tenor.gif",
                "https://images-ext-1.discordapp.net/external/MPx_UppCsstiEPGzil1N9HsWQnzEdIPXubS95-7-KzE/%3Fitemid%3D16980741/https/media1.tenor.com/images/86a20dbf1dacf6a539569057e20eaeaf/tenor.gif",
                "https://images-ext-2.discordapp.net/external/0EIJruOSuC9KQgbYoOOEQypnv7nvUwOKm2gJjBmgnPo/%3Fitemid%3D7189175/https/media1.tenor.com/images/f64f4e0d22303666d9548623292f0139/tenor.gif",
                "https://images-ext-2.discordapp.net/external/z22EfQQmogLMMuuLPdRaln5LJMTHQ-2M0oF8v--EZY8/%3Fitemid%3D18996997/https/media1.tenor.com/images/1b532e3c2000ac2c4fb3ce033f3a7ccd/tenor.gif",
                "https://images-ext-1.discordapp.net/external/08wWnGRGm65gVFBY557g6knFqNUh_toMu3VHIs-k_G4/%3Fitemid%3D14066854/https/media1.tenor.com/images/1cd2bbd72c77495229f0ff3551b1678f/tenor.gif",
                "https://images-ext-2.discordapp.net/external/MMnPqKTRN4bmkwYZFHrB_xP3vFFKGBKOu4qfd8QcIxs/%3Fitemid%3D15261239/https/media1.tenor.com/images/1b27c69585088b0e99e7007029401852/tenor.gif",
                "https://images-ext-2.discordapp.net/external/XU2wm8ou561yqinnuP2LsNakwTSS19Unzw4m7Lwn3oE/%3Fitemid%3D10592083/https/media1.tenor.com/images/11b756289eec236b3cd8522986bc23dd/tenor.gif",
                "https://images-ext-2.discordapp.net/external/TKLjf4fh-gPUGz5rqi43wvQsOEuYdQE8t252ohpV2ac/%3Fitemid%3D17897599/https/media1.tenor.com/images/8fd2c922b1bcbbe4ca9705d3f18f52b5/tenor.gif",
                "https://images-ext-2.discordapp.net/external/h83u76OvnriZ7afvqZ1fCz6dJUFkD8KBKTQDYfA6Vas/%3Fitemid%3D19371759/https/media1.tenor.com/images/f5e919bfd6afb6b2053bd938443fc2e9/tenor.gif",
                "https://images-ext-2.discordapp.net/external/mkgfJLKSyEBM4WEKn1rSDgvPZVixWX3oRXSlGdaVWNM/%3Fitemid%3D9136391/https/media1.tenor.com/images/b87f8b1e2732c534a00937ffb24baa79/tenor.gif",
                "https://images-ext-2.discordapp.net/external/C6SiaGIvPgKsqVV3x3t1OJXek2u11U1Qneplum0aoxE/%3Fitemid%3D17789653/https/media1.tenor.com/images/99622a9f154d4147abaf5d3599e01ff9/tenor.gif",
                "https://images-ext-2.discordapp.net/external/_iucgRsucqeB_vceyHC34iNdT4_BcH74GARjBhm0TbE/%3Fitemid%3D12070724/https/media1.tenor.com/images/8503ea13c80b50a0ed9320bdf317f925/tenor.gif",
                "https://images-ext-2.discordapp.net/external/pKEEV4dnDAId2EVxdcNhNOzHGSP25as_yybQ17cKGFc/%3Fitemid%3D15150359/https/media1.tenor.com/images/31f85fdb5dde1c383de6ada6540b2020/tenor.gif",
                "https://images-ext-1.discordapp.net/external/9bGqfmZg3CZP1kYnrNIG1k3MUpMcGvTRQiT54gCPaEY/%3Fitemid%3D14844150/https/media1.tenor.com/images/205cde7485168c9d7aac25106a80eece/tenor.gif",
                "https://images-ext-2.discordapp.net/external/NBc-nqT40aiCKGpT0IJupvnU7pIuAIsevwU8D3xdyt4/%3Fitemid%3D14301347/https/media1.tenor.com/images/e00b951f034b08c3c3bf88e7d22aec57/tenor.gif",
                "https://images-ext-1.discordapp.net/external/HwlmE9KbNY0nAJW-7z75ms2tJSNhc6K8PNg5VUq67gE/%3Fitemid%3D17907296/https/media1.tenor.com/images/1a8fdd0d554f187eea34dec252c8a411/tenor.gif",
                "https://images-ext-1.discordapp.net/external/5LADATezVgnP0Gk5dLdXfgnI1AdTwo9BTOpsoaMh2Ko/%3Fitemid%3D14637016/https/media1.tenor.com/images/4db088cfc73a5ee19968fda53be6b446/tenor.gif",
                "https://images-ext-2.discordapp.net/external/ntTSKfK0BeNy3nAclTl5WeSesdV6zQBvvrpZNaNRG2A/%3Fitemid%3D14246498/https/media1.tenor.com/images/969f0f462e4b7350da543f0231ba94cb/tenor.gif",
                "https://images-ext-1.discordapp.net/external/q5s6oHF9R6FwOHPrUxly-Oi0nO-YUmO7BQrtXl-8CNI/%3Fitemid%3D7552087/https/media1.tenor.com/images/03ff67460b3e97cf13aac5d45a072d22/tenor.gif",
                "https://images-ext-1.discordapp.net/external/2TAL2AoHlWYA2U4lStmtWb8CCo0S417XnedHFaz9uaw/%3Fitemid%3D19674705/https/media1.tenor.com/images/f7b6be96e8ebb23319b43304da0e1118/tenor.gif"
          ]

          t = Translator(interaction.guild.id, loadStrings=True)
          if interaction.user == user:
              title = t.getLocalString("hugLonely", [("user", interaction.user.display_name)])
              e = discord.Embed(title=title)
              link = "https://media1.tenor.com/images/1506349f38bf33760d45bde9b9b263a4/tenor.gif"
              e.set_image(url=link)
          else:
              title = t.getLocalString("hugUser", [("user", user.display_name), ("otherUser", interaction.user.display_name)])
              e = discord.Embed(title=title)
              link = str(hugList[random.randint(0, len(hugList) - 1)])
              e.set_image(url= link)
          await interaction.response.send_message(content = (user.mention or None) + "\n" + link,embed=e)


    @app_commands.command(name="stand", description = "Displays your assigned JJBA stand, your stand is bounded to you and won't change.")
    async def stand(self, interaction: discord.Interaction):
      if not interaction.user.bot :
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT stand_id FROM user_stand WHERE user_id = ?", (interaction.user.id, ))
        stand_id = await cursor.fetchone()
        if stand_id == None:
          stand_id = random.randint(1, 32)
          await cursor.execute("INSERT INTO user_stand(user_id, stand_id) VALUES(?, ?)", (interaction.user.id, stand_id))
        else:
          stand_id = stand_id[0]
        await cursor.execute("SELECT stand_name, stand_link FROM stands WHERE stand_id = ?", (stand_id, ))
        stand = await cursor.fetchone()
        await connection.commit()
        await close_conn(connection, cursor)
        t = Translator(interaction.guild.id, loadStrings = True)
        title = t.getLocalString("userStand", [("user", interaction.user.display_name), ("standName", stand[0])])
        e = discord.Embed(title = title, colour=discord.Colour(0x635f))
        e.set_image(url=stand[1])
        await interaction.response.send_message (content = stand[1], embed = e)
