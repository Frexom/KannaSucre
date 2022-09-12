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
      await cursor.execute("SELECT user_level, user_xp FROM users WHERE user_id = ?", (user.id, ))
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
        draw.ellipse((0, 0, 49, 49), fill=255)
        image.paste(bronze, (350, 52), mask_im)

        if stats[0]>=50:
          silver = Image.open("./files/LevelCommand/KannaSilver.png")
          image.paste(silver, (405, 52), mask_im)
          if stats[0]>=100:
            gold = Image.open("./files/LevelCommand/KannaGold.png")
            image.paste(gold, (460, 52), mask_im)

      font = ImageFont.truetype("./files/LevelCommand/coolvetica.ttf", size=40)
      d = ImageDraw.Draw(image)
      message = str(user.name) + "\nLevel " + str(stats[0]) + "\n" + str(stats[1]) + "/" +str(500*stats[0]) + "XP"
      d.text((100, 50), message, font=font, fill= (90,90,90))
      image.save("./files/LevelCommand/stats" + str(user.id) + ".png")
      await ctx.send(file = discord.File("./files/LevelCommand/stats" + str(user.id) + ".png"))
    else:
      await ctx.send("This command isn't supported for bots.")
