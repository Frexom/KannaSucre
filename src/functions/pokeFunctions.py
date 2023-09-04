import time

import discord

from src.resources.adapter import ContextAdapter
from src.resources.pokemon import POKE_COUNT, Pokedex, Pokemon, RandomPokemon
from src.resources.ui import ClearView


async def pokeFunction(bot, interaction: ContextAdapter):
    if not interaction.getAuthor().bot:
        # Not doidng it may cause bugs
        await interaction.defer()

        userID = interaction.getAuthor().id
        userName = interaction.getAuthor().display_name

        cursor = await bot.connection.cursor()
        await cursor.execute(
            "SELECT user_last_roll_datetime, user_pity, link_type FROM dis_user WHERE user_id =?",
            (userID,),
        )
        data = await cursor.fetchone()

        last_roll = data[0]
        pity = data[1]
        linkType = data[2]
        now = time.time()
        time_since = int(now - last_roll)

        if time_since > 7200 or pity >= 1:
            if time_since < 7200:
                pity -= 1
                await cursor.execute(
                    "UPDATE dis_user SET user_pity = ? WHERE user_id = ?",
                    (pity, userID),
                )
            else:
                await cursor.execute(
                    "UPDATE dis_user SET user_last_roll_datetime = ? WHERE user_id = ?",
                    (now, userID),
                )

            pokemon = RandomPokemon(bot, interaction=interaction, linkType=linkType)

            await cursor.execute(
                "SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?",
                (userID, pokemon.id, pokemon.alt),
            )
            is_obtained = await cursor.fetchone()

            # Second chance
            if is_obtained:
                pokemon = RandomPokemon(bot, interaction=interaction, linkType=linkType)

            await cursor.execute(
                "SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?",
                (userID, pokemon.id, pokemon.alt),
            )
            is_obtained = await cursor.fetchone()
            await cursor.execute(
                "SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ?",
                (userID, pokemon.id),
            )
            is_pokedex = await cursor.fetchone()

            link = pokemon.link
            desc = ""

            # Pokémon form
            if pokemon.label != "Normal" and pokemon.label != "Female" and pokemon.label != "Male":
                desc += bot.translator.getLocalString(
                    interaction, "pokeForm", [("form", pokemon.label)]
                )
                desc += "\n"

            desc += bot.translator.getLocalString(
                interaction, "pokeRarity", [("rarity", pokemon.rarity[1])]
            )

            # isShiny
            if pokemon.shiny:
                desc += "\n"
                desc += bot.translator.getLocalString(interaction, "isShiny", [])

            # New Form
            if is_obtained == None and (is_pokedex):
                desc += "\n"
                desc += bot.translator.getLocalString(interaction, "pokeNewForm", [])

            # New Pokémon
            if is_obtained == None:
                await cursor.execute(
                    "INSERT INTO poke_obtained (user_id, dex_id, form_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)",
                    (userID, pokemon.id, pokemon.alt, int(pokemon.shiny), now),
                )

            # Pokemon already captured but shiny
            elif is_obtained[3] == 0 and pokemon.shiny:
                await cursor.execute(
                    "UPDATE poke_obtained SET is_shiny = 1 WHERE user_id = ? and dex_id = ?",
                    (userID, pokemon.id),
                )

            # Pokemon already captured
            else:
                desc += "\n"
                desc += bot.translator.getLocalString(interaction, "pokeAlready", [])
                desc += "\n"
                desc += bot.translator.getLocalString(
                    interaction,
                    "pokeExtraRolls",
                    [("number", pokemon.rarity[0] * 0.25)],
                )
                await cursor.execute(
                    "UPDATE dis_user SET user_pity = ? WHERE user_id = ?",
                    (pity + 0.25 * pokemon.rarity[0], userID),
                )

            await bot.connection.commit()
            title = bot.translator.getLocalString(
                interaction,
                "pokeCatch",
                [("user", userName), ("pokeName", pokemon.name)],
            )
            e = discord.Embed(title=title, description=desc)
            e.set_image(url=link)
            await interaction.followupSend(content=link, embed=e)
            await cursor.close()

        else:
            await rollsFunction(bot, interaction)


async def pokeinfoFunction(bot, interaction: ContextAdapter, id: int = None, name: str = None):
    if not interaction.getAuthor().bot:
        if id is not None or name is not None:
            if name is not None:
                poke_id = bot.translator.getPokeIdByName(interaction, name.lower())
            else:
                poke_id = id

            # If poke_id is Illegal
            if poke_id > POKE_COUNT or poke_id <= 0:
                title = bot.translator.getLocalString(interaction, "pokeinfoNotFound", [])
                description = bot.translator.getLocalString(interaction, "pokeinfoNoSuch", [])
                e = discord.Embed(title=title, description=description)
                await interaction.sendMessage(embed=e)
                return

            cursor = await bot.connection.cursor()
            await cursor.execute(
                "SELECT link_type FROM dis_user WHERE user_id = ?",
                (interaction.getAuthor().id,),
            )
            linkType = await cursor.fetchone()
            await cursor.close()
            linkType = linkType[0]
            pokemon = Pokemon(bot, interaction=interaction, linkType=linkType, pokeID=poke_id)
            buttonView = ClearView(interaction, timeout=90)

            # Callback definition, and buttons generation
            label = bot.translator.getLocalString(interaction, "buttonEvolve", [])
            evolveButton = discord.ui.Button(
                label=label, style=discord.ButtonStyle.secondary, emoji="⏫", row=1
            )
            prev = discord.ui.Button(
                label=" ", style=discord.ButtonStyle.primary, emoji="⬅️", row=2
            )
            label = bot.translator.getLocalString(interaction, "buttonShiny", [])
            shinyButton = discord.ui.Button(
                label=label, style=discord.ButtonStyle.secondary, emoji="✨", row=2
            )
            next = discord.ui.Button(
                label=" ", style=discord.ButtonStyle.primary, emoji="➡️", row=2
            )
            label = bot.translator.getLocalString(interaction, "buttonDevolve", [])
            devolveButton = discord.ui.Button(
                label=label, style=discord.ButtonStyle.secondary, emoji="⏬", row=3
            )
            sugimori = discord.ui.Button(label="Sprites", style=discord.ButtonStyle.success, row=3)

            filler1 = discord.ui.Button(label="⠀⠀⠀", row=1, disabled=True)
            filler2 = discord.ui.Button(label="⠀⠀⠀", row=1, disabled=True)
            filler3 = discord.ui.Button(label="⠀⠀⠀", row=3, disabled=True)

            async def prevCallback(interaction):
                nonlocal pokemon
                interaction = ContextAdapter(interaction)

                pokemon.prev_alt()
                await interaction.editMessage(
                    content=pokemon.getLink(),
                    embed=pokemon.get_pokeinfo_embed(),
                )
                await interaction.defer()

            prev.callback = prevCallback

            async def devolveCallback(interaction):
                nonlocal pokemon
                interaction = ContextAdapter(interaction)

                if pokemon.devolve():
                    await interaction.editMessage(
                        content=pokemon.getLink(),
                        embed=pokemon.get_pokeinfo_embed(),
                    )
                await interaction.defer()

            devolveButton.callback = devolveCallback

            async def shinyCallback(interaction):
                nonlocal pokemon
                interaction = ContextAdapter(interaction)

                pokemon.shiny = not pokemon.shiny
                await interaction.editMessage(
                    content=pokemon.getLink(),
                    embed=pokemon.get_pokeinfo_embed(),
                )
                await interaction.defer()

            shinyButton.callback = shinyCallback

            async def evolveCallback(interaction: ContextAdapter):
                nonlocal pokemon, buttonView
                interaction = ContextAdapter(interaction)

                await interaction.defer()
                if pokemon.evolutions is not None:
                    if len(pokemon.evolutions) > 1:
                        dropdown = PokeDropdown(interaction, pokemon, buttonView)

                        evoView = ClearView(interaction, timeout=90)
                        evoView.add_item(dropdown)

                        await interaction.editMessage(view=evoView)
                    else:
                        pokemon.evolve()
                        await interaction.editMessage(
                            content=pokemon.getLink(),
                            embed=pokemon.get_pokeinfo_embed(),
                        )

            evolveButton.callback = evolveCallback

            async def nextCallback(interaction):
                nonlocal pokemon
                interaction = ContextAdapter(interaction)

                pokemon.next_alt()
                await interaction.editMessage(
                    content=pokemon.getLink(),
                    embed=pokemon.get_pokeinfo_embed(),
                )
                await interaction.defer()

            next.callback = nextCallback

            async def sugimoriCallback(interaction):
                nonlocal pokemon
                interaction = ContextAdapter(interaction)

                pokemon.switchType()
                await interaction.editMessage(
                    content=pokemon.getLink(),
                    embed=pokemon.get_pokeinfo_embed(),
                )
                content = bot.translator.getLocalString(
                    interaction, f"pokeinfoLinktype{(pokemon.linkType-1)%2}", []
                )

                await interaction.sendMessage(content=content, ephemeral=True)

                cursor = await bot.connection.cursor()
                await cursor.execute(
                    "UPDATE dis_user SET link_type = ? WHERE user_id = ?",
                    (pokemon.linkType, interaction.getAuthor().id),
                )
                await bot.connection.commit()
                await cursor.close()

            sugimori.callback = sugimoriCallback

            buttonView.add_item(filler1)
            buttonView.add_item(evolveButton)
            buttonView.add_item(filler2)
            buttonView.add_item(prev)
            buttonView.add_item(shinyButton)
            buttonView.add_item(next)
            buttonView.add_item(filler3)
            buttonView.add_item(devolveButton)
            buttonView.add_item(sugimori)

            await interaction.sendMessage(
                content=pokemon.getLink(),
                embed=pokemon.get_pokeinfo_embed(),
                view=buttonView,
            )

        else:
            content = bot.translator.getLocalString(interaction, "pokeinfoInput", [])
            await interaction.sendMessage(content=content)


async def rollsFunction(bot, interaction: ContextAdapter):
    await interaction.defer()
    cursor = await bot.connection.cursor()
    await cursor.execute(
        "SELECT user_last_roll_datetime, user_pity FROM dis_user WHERE user_id =?",
        (interaction.getAuthor().id,),
    )
    data = await cursor.fetchone()
    last_roll = data[0]
    pity = data[1]
    now = time.time()
    time_since = int(now - last_roll)
    time_left = int(7200 - time_since)
    userName = interaction.getAuthor().display_name
    if time_left <= 0:
        content = bot.translator.getLocalString(
            interaction, "rollsAvailable", [("user", userName), ("number", pity)]
        )
        await interaction.sendMessage(content=content)
    elif time_left > 3600:
        time_left -= 3600
        time_left = int(time_left / 60)
        content = bot.translator.getLocalString(
            interaction,
            "rollsHours",
            [
                ("user", userName),
                ("hours", 1),
                ("minutes", time_left),
                ("number", pity),
            ],
        )
        await interaction.sendMessage(content=content)
    else:
        time_left += 60
        time_left = int(time_left / 60)
        content = bot.translator.getLocalString(
            interaction,
            "rollsMinutes",
            [("user", userName), ("minutes", time_left), ("number", pity)],
        )
        await interaction.followupSend(content=content)
    await cursor.close()


async def pokedexFunction(
    bot, interaction: ContextAdapter, user: discord.User = None, page: int = 1
):
    if not interaction.getAuthor().bot:
        if user is None:
            user = interaction.getAuthor()
        if not user.bot:
            closedView = ClearView(interaction, timeout=90)
            openedView = ClearView(interaction, timeout=90)
            pokedex = Pokedex(bot, interaction, user, page - 1)

            label = bot.translator.getLocalString(interaction, "buttonOpen", [])
            open = discord.ui.Button(label=label, emoji="🌐")

            async def openCallback(interaction):
                nonlocal openedView, pokedex
                interaction = ContextAdapter(interaction)

                pokedex.open()
                await interaction.editMessage(embed=pokedex.embed, view=openedView)
                await interaction.defer()

            open.callback = openCallback

            label = bot.translator.getLocalString(interaction, "buttonShinies", [])
            shinies = discord.ui.Button(label=label, emoji="✨")

            async def shiniesCallback(interaction):
                nonlocal openedView, pokedex
                interaction = ContextAdapter(interaction)

                pokedex.toggleShiny()
                pokedex.open()
                await interaction.editMessage(embed=pokedex.embed, view=openedView)
                await interaction.defer()

            shinies.callback = shiniesCallback

            label = bot.translator.getLocalString(interaction, "buttonClose", [])
            close = discord.ui.Button(label=label, emoji="🌐")

            async def closeCallback(interaction):
                nonlocal closedView, pokedex
                interaction = ContextAdapter(interaction)

                pokedex.close()
                await interaction.editMessage(embed=pokedex.embed, view=closedView)
                await interaction.defer()

            close.callback = closeCallback

            prev = discord.ui.Button(label=" ", emoji="⬅️")

            async def prevCallback(interaction):
                nonlocal pokedex
                interaction = ContextAdapter(interaction)

                pokedex.prev()
                await interaction.editMessage(embed=pokedex.embed)
                await interaction.defer()

            prev.callback = prevCallback

            next = discord.ui.Button(label=" ", emoji="➡️")

            async def nextCallback(interaction):
                nonlocal pokedex
                interaction = ContextAdapter(interaction)

                pokedex.next()
                await interaction.editMessage(embed=pokedex.embed)
                await interaction.defer()

            next.callback = nextCallback

            closedView.add_item(open)
            closedView.add_item(shinies)
            openedView.add_item(prev)
            openedView.add_item(close)
            openedView.add_item(next)

            await interaction.sendMessage(embed=pokedex.embed, view=closedView)
        else:
            content = bot.translator.getLocalString(interaction, "commandBot", [])
            await interaction.sendMessage(content=content)


async def pokerankFunction(bot, interaction: ContextAdapter):
    if not interaction.getAuthor().bot:
        await interaction.defer()

        cursor = await bot.connection.cursor()
        await cursor.execute(
            "SELECT COUNT(DISTINCT dex_id) as nbPoke, user_name  FROM poke_obtained JOIN dis_user USING(user_id) GROUP BY user_id ORDER BY nbPoke desc limit 10"
        )
        result = await cursor.fetchall()
        await cursor.close()
        result_list = []
        for i in range(len(result)):
            result_list.append([result[i][0], result[i][1]])
        description = ""
        i = 0
        limit = 10
        while i != len(result_list) and i < 10:
            description += (
                str(i + 1)
                + " - "
                + result_list[i][1]
                + " - "
                + str(result_list[i][0])
                + "/"
                + str(POKE_COUNT)
                + "\n"
            )
            i += 1

        title = bot.translator.getLocalString(interaction, "pokerank", [])
        embed = discord.Embed(title=title, colour=discord.Colour(0x635F))
        embed.set_thumbnail(url=bot.user.avatar)
        name = bot.translator.getLocalString(interaction, "pokerankRanking", [])
        embed.add_field(name=name, value=description)
        await interaction.followupSend(embed=embed)
