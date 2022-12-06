from PIL import Image, ImageFont, ImageDraw

from connection import *
from mentions import *
from prefix import *
from bot import *

sys.path.append("../ressources")

@bot.command(name="level")
async def level(ctx):
    user = get_target(ctx)
    if not user.bot and not ctx.author.bot:
      await user.display_avatar.save(fp="./files/LevelCommand/Users/" + str(user.id) + ".png")
      connection, cursor = await get_conn("./files/ressources/bot.db")
      await cursor.execute("SELECT user_level, user_xp FROM dis_user WHERE user_id = ?", (user.id, ))
      stats = await cursor.fetchone()
      await close_conn(connection, cursor)

      image = Image.open("./files/LevelCommand/Base.png")
      ProfilePic = Image.open("./files/LevelCommand/Users/" + str(user.id) + ".png")
      ProfilePic = ProfilePic.resize((190, 190))
      mask_im = Image.new("L", ProfilePic.size, 0)
      draw = ImageDraw.Draw(mask_im)
      draw.ellipse((0, 0, 190, 190), fill=255)
      image.paste(ProfilePic, (556, 30), mask_im)

      if stats[0]>=20:
        bronze = Image.open("./files/LevelCommand/KannaBronze.png")
        mask_im = Image.new("L", bronze.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 48, 48), fill=255)
        image.paste(bronze, (480, 180), mask_im)

        if stats[0]>=50:
          silver = Image.open("./files/LevelCommand/KannaSilver.png")
          image.paste(silver, (490, 180), mask_im)
          if stats[0]>=100:
            gold = Image.open("./files/LevelCommand/KannaGold.png")
            image.paste(gold, (500, 180), mask_im)

      if len(user.display_name) > 20:
          nameFont = ImageFont.truetype("./files/LevelCommand/coolvetica.ttf", size=30)
      else:
          nameFont = ImageFont.truetype("./files/LevelCommand/coolvetica.ttf", size=40)

      font = ImageFont.truetype("./files/LevelCommand/coolvetica.ttf", size=40)
      d = ImageDraw.Draw(image)
      level = "Level " + str(stats[0]) + "\n" + str(stats[1]) + "/" +str(500*stats[0]) + "XP"
      d.text((80, 50), user.display_name, font=nameFont, fill= (90,90,90))
      d.multiline_text((80, 95), level, font=font, fill= (90,90,90))
      image.save("./files/LevelCommand/Users/stats" + str(user.id) + ".png")
      await ctx.send(file = discord.File("./files/LevelCommand/Users/stats" + str(user.id) + ".png"))
    else:
      t = Translator(ctx.guild.id, loadStrings=True)
      content = t.getLocalString("commandBot", [])
      await ctx.send(content = content)
