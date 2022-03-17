import discord
from connection import *
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw
from prefix import *
from mentions import *



async def level(ctx):
  if not ctx.message.author.bot :
    user = get_target(ctx)
    if not user.bot:
      await user.avatar_url_as(format="png").save(fp="LevelCommand/Users/" + str(user.id) + ".png")

      connection, cursor = await get_conn()
      await cursor.execute("SELECT user_level, user_xp FROM users WHERE user_id = ?", (user.id, ))
      stats = await cursor.fetchone()
      await close_conn(connection, cursor)

      image = Image.open("LevelCommand/Base.png")
      ProfilePic = Image.open("LevelCommand/Users/" + str(user.id) + ".png")
      ProfilePic = ProfilePic.resize((190, 190))
      mask_im = Image.new("L", ProfilePic.size, 0)
      draw = ImageDraw.Draw(mask_im)
      draw.ellipse((0, 0, 190, 190), fill=255)
      image.paste(ProfilePic, (556, 30), mask_im)

      if stats[0]>=20:
        bronze = Image.open("LevelCommand/KannaBronze.png")
        mask_im = Image.new("L", bronze.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 49, 49), fill=255)
        image.paste(bronze, (350, 52), mask_im)

        if stats[0]>=50:
          silver = Image.open("LevelCommand/KannaSilver.png")
          image.paste(silver, (405, 52), mask_im)
          if stats[0]>=100:
            gold = Image.open("LevelCommand/KannaGold.png")
            image.paste(gold, (460, 52), mask_im)

      font = ImageFont.truetype("LevelCommand/coolvetica.ttf", size=40)
      d = ImageDraw.Draw(image)
      message = str(user.name) + "\nLevel " + str(stats[0]) + "\n" + str(stats[1]) + "/" +str(500*stats[0]) + "XP"
      d.text((100, 50), message, font=font, fill= (90,90,90))
      image.save("LevelCommand/stats" + str(user.id) + ".png")
      await ctx.send(file = discord.File("LevelCommand/stats" + str(user.id) + ".png"))
    else:
      await ctx.send("This command isn't supported for bots.")