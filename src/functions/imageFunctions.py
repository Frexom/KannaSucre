from PIL import Image, ImageDraw, ImageFont

from src.resources.bot import *
from src.resources.connection import *
from src.resources.mentions import *
from src.resources.prefix import *


async def levelFunction(interaction: ContextAdapter, user: discord.User = None):
    # If no user specified, user is author
    if user is None:
        user = interaction.getAuthor()

    if not user.bot and not interaction.getAuthor().bot:

        cursor = await bot.connection.cursor()
        await cursor.execute(
            "SELECT user_level, user_xp, (SELECT COUNT(*) FROM com_history WHERE user_id = ?) as nbCommands FROM dis_user WHERE user_id = ?;",
            (user.id, user.id),
        )
        stats = await cursor.fetchone()
        await cursor.close()

        # Pasting pfp on level image
        await user.display_avatar.save(
            fp="src/LevelCommand/Users/" + str(user.id) + ".png"
        )
        image = Image.open("src/LevelCommand/Base.png")
        ProfilePic = Image.open("src/LevelCommand/Users/" + str(user.id) + ".png")
        ProfilePic = ProfilePic.resize((190, 190))
        mask_im = Image.new("L", ProfilePic.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 190, 190), fill=255)
        image.paste(ProfilePic, (556, 30), mask_im)

        # Applying medals
        if stats[0] >= 20:
            bronze = Image.open("src/LevelCommand/KannaBronze.png")
            mask_im = Image.new("L", bronze.size, 0)
            draw = ImageDraw.Draw(mask_im)
            draw.ellipse((0, 0, 48, 48), fill=255)
            image.paste(bronze, (480, 180), mask_im)

            if stats[0] >= 50:
                silver = Image.open("src/LevelCommand/KannaSilver.png")
                image.paste(silver, (490, 180), mask_im)

                if stats[0] >= 100:
                    gold = Image.open("src/LevelCommand/KannaGold.png")
                    image.paste(gold, (500, 180), mask_im)

        # Shrink the font's size if username is too long
        if len(user.display_name) > 20:
            font = ImageFont.truetype("src/LevelCommand/coolvetica.ttf", size=30)
        else:
            font = ImageFont.truetype("src/LevelCommand/coolvetica.ttf", size=40)

        # Create rendering
        d = ImageDraw.Draw(image)

        # Render name
        d.text((80, 30), user.display_name, font=font, fill=(90, 90, 90))

        # Render level
        font = ImageFont.truetype("src/LevelCommand/coolvetica.ttf", size=40)
        level = (
            "Level "
            + str(stats[0])
            + "\n"
            + str(stats[1])
            + "/"
            + str(500 * stats[0])
            + "XP"
        )
        d.multiline_text((80, 75), level, font=font, fill=(90, 90, 90))

        # Render commands count
        font = ImageFont.truetype("src/LevelCommand/coolvetica.ttf", size=28)
        d.text(
            (80, 200), "Commands run: " + str(stats[2]), font=font, fill=(120, 120, 120)
        )

        # Save and send file
        image.save("src/LevelCommand/Users/stats" + str(user.id) + ".png")
        await interaction.sendMessage(
            file=discord.File("src/LevelCommand/Users/stats" + str(user.id) + ".png")
        )

    # If user if bot
    else:
        content = bot.translator.getLocalString(interaction, "commandBot", [])
        await interaction.sendMessage(content=content)
