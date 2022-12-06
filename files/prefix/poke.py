from connection import *
from mentions import *
from pokemon import *
from prefix import *
from bot import *
from ui import *

sys.path.append("../ressources")


@bot.command(name="poke")
async def poke(ctx):
  if not ctx.author.bot :
    await ctx.channel.typing()


    userID = ctx.author.id
    userName = ctx.author.display_name or ctx.author.name

    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM dis_user WHERE user_id =?", (userID, ))
    data = await cursor.fetchone()

    last_roll = data[0]
    pity = data[1]
    now = time.time()
    time_since = int(now - last_roll)

    t = Translator(ctx.guild.id, loadStrings = True)
    if time_since > 7200 or pity >= 1:
        if time_since < 7200:
            pity -= 1
            await cursor.execute("UPDATE dis_user SET user_pity = ? WHERE user_id = ?", (pity, userID))
        else:
            await cursor.execute("UPDATE dis_user SET user_last_roll_datetime = ? WHERE user_id = ?", (now, userID))
        await connection.commit()

        pokemon = Pokemon(guildID = ctx.guild.id)

        await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?", (userID, pokemon.id, pokemon.alt ))
        is_obtained = await cursor.fetchone()

        #Second chance
        if(is_obtained):
                pokemon = Pokemon(guildID = ctx.guild.id)

        await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?", (userID, pokemon.id, pokemon.alt ))
        is_obtained = await cursor.fetchone()
        await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ?", (userID, pokemon.id))
        is_pokedex = await cursor.fetchone()



        shiny_string = ""
        form_string = ""
        link = pokemon.link


        pokeRarity = t.getLocalString("pokeRarity", [("rarity", pokemon.rarity[1])])
        if pokemon.shiny:
            shiny_string = "\n"
            shiny_string += t.getLocalString("isShiny", [])

        #New Form
        if(is_obtained == None and (is_pokedex)):
            form_string = "\n"
            form_string += t.getLocalString("pokeNewForm", [])

        #New Pokémon
        if is_obtained == None:
            await cursor.execute("INSERT INTO poke_obtained (user_id, dex_id, form_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (userID, pokemon.id, pokemon.alt, int(pokemon.shiny), now))
            desc = pokeRarity + form_string + shiny_string

        #Pokemon already captured but shiny
        elif (is_obtained[3] == 0 and pokemon.shiny):
            await cursor.execute("UPDATE poke_obtained SET is_shiny = 1 WHERE user_id = ? and dex_id = ?", (userID, pokemon.id))
            desc = pokeRarity + form_string + shiny_string

        #Pokemon already captured
        else:
            pokeAlready = "\n"
            pokeAlready += t.getLocalString("pokeAlready", [])
            pokeExtraRolls = t.getLocalString("pokeExtraRolls", [("number", pokemon.rarity[0]*0.25)])
            desc = pokeRarity + shiny_string + pokeAlready + "\n" +pokeExtraRolls
            await cursor.execute("UPDATE dis_user SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon.rarity[0], userID))

        await connection.commit()
        title = t.getLocalString("pokeCatch", [("user", userName), ("pokeName", pokemon.name)])
        e = discord.Embed(title = title, description = desc)
        e.set_image(url=link)
        await ctx.send(content = link, embed = e)

    else:
        time_left = int(7200 - time_since)
        if time_left > 3600:
            time_left -= 3600
            time_left = int(time_left/60)
            content = t.getLocalString("rollsHours", [("user", userName), ("hours", 1), ("minutes", time_left), ("number", pity)])
        else:
            time_left += 60
            time_left = int(time_left/60)
            content = t.getLocalString("rollsMinutes", [("user", userName), ("minutes", time_left), ("number", pity)])
        await ctx.send(content = content)
    await close_conn(connection, cursor)


@bot.command(name="pokeinfo")
async def pokeinfo(ctx):
    if not ctx.author.bot:
        message = ctx.message.content.split(" ")
        if len(message) > 1:
            pokemon = message[1]
            if not pokemon.isdecimal():
                poke_id = t.getPokeIdByName(pokemon.lower())
            else:
                poke_id = int(message[1])

            t = Translator(ctx.guild.id, loadStrings = True, loadPoke = True)

            #If poke_id is Illegal
            if poke_id > poke_count or poke_id <= 0 :
                title = t.getLocalString("pokeinfoNotFound", [])
                description = t.getLocalString("pokeinfoNoSuch", [])
                e = discord.Embed(title = title, description = description)
                await ctx.send(embed = e)
                return


            pokemon = Pokemon(guildID = ctx.guild.id, pokeID = poke_id)
            buttonView = pokeView(90)

        #Callback definition, and buttons generation
            evolveButton = discord.ui.Button(label = "Evolve⠀", style = discord.ButtonStyle.secondary, emoji = "⏫", row = 1)
            prev = discord.ui.Button(label = " ", style = discord.ButtonStyle.primary, emoji = "⬅️", row = 2)
            shinyButton = discord.ui.Button(label = "⠀Shiny", style = discord.ButtonStyle.secondary, emoji = "✨", row = 2)
            next = discord.ui.Button(label = " ", style = discord.ButtonStyle.primary, emoji = "➡️", row = 2)
            devolveButton = discord.ui.Button(label = "Devolve", style = discord.ButtonStyle.secondary, emoji = "⏬", row = 3)

            filler1 = discord.ui.Button(label = "⠀⠀⠀", row = 1, disabled = True)
            filler2 = discord.ui.Button(label = "⠀⠀⠀", row = 1, disabled = True)
            filler3 = discord.ui.Button(label = "⠀⠀⠀", row = 3, disabled = True)
            filler4 = discord.ui.Button(label = "⠀⠀⠀", row = 3, disabled = True)


            async def prevCallback(interaction: discord.Interaction):
                nonlocal pokemon
                pokemon.prev_alt()
                await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                await interaction.response.defer()
            prev.callback = prevCallback


            async def devolveCallback(interaction: discord.Interaction):
                nonlocal pokemon
                if pokemon.devolution is not None:
                    pokemon.devolve()
                    await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                await interaction.response.defer()
            devolveButton.callback = devolveCallback


            async def shinyCallback(interaction: discord.Interaction):
                nonlocal pokemon
                pokemon.shiny = not pokemon.shiny
                await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                await interaction.response.defer()
            shinyButton.callback = shinyCallback


            async def evolveCallback(interaction: discord.Interaction):
                nonlocal pokemon, buttonView
                if pokemon.evolutions is not None:
                    if len(pokemon.evolutions) > 1:
                        dropdown = PokeDropdown(pokemon, buttonView)

                        evoView = pokeView(90)
                        evoView.setMessage(buttonView.message)
                        evoView.add_item(dropdown)

                        await interaction.message.edit(view = evoView)
                    else:
                        pokemon.evolve()
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                await interaction.response.defer()
            evolveButton.callback = evolveCallback



            async def nextCallback(interaction: discord.Interaction):
                nonlocal pokemon
                pokemon.next_alt()
                await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                await interaction.response.defer()
            next.callback = nextCallback


            buttonView.add_item(filler1)
            buttonView.add_item(evolveButton)
            buttonView.add_item(filler2)
            buttonView.add_item(prev)
            buttonView.add_item(shinyButton)
            buttonView.add_item(next)
            buttonView.add_item(filler3)
            buttonView.add_item(devolveButton)
            buttonView.add_item(filler4)

            message = await ctx.send(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed(), view = buttonView)
            buttonView.setMessage(message)

        else:
            content = t.getLocalString("pokeinfoInput", [])
            await ctx.response.send_message(content = content)


@bot.command(name="rolls")
async def rolls(ctx):
    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM dis_user WHERE user_id =?", (ctx.author.id, ))
    data = await cursor.fetchone()
    last_roll, pity = data[0], data[1]
    now = time.time()
    time_since = int(now - last_roll)
    time_left = int(7200 - time_since)
    userName = ctx.author.display_name or ctx.author.name
    t = Translator(ctx.guild.id, loadStrings = True)

    if time_left <= 0:
        content = t.getLocalString("rollsAvailable", [("user", userName), ("number", pity)])
        await ctx.send(content = content)
    elif time_left > 3600:
        time_left -= 3600
        time_left = int(time_left/60)
        content = t.getLocalString("rollsHours", [("user", userName), ("hours", 1), ("minutes", time_left), ("number", pity)])
        await ctx.send(content = content)
    else:
        time_left += 60
        time_left = int(time_left/60)
        content = t.getLocalString("rollsMinutes", [("user", userName), ("minutes", time_left), ("number", pity)])
        await ctx.send(content = content)
    await close_conn(connection, cursor)


@bot.command(name="pokedex")
async def pokedex(ctx):
    if not ctx.author.bot :
        user = get_target(ctx)
        if not user.bot:
            message = ctx.message.content.split(" ")
            page = 1
            if len(message) > 1 and message[1].isdecimal() :
                page = int(message[1])
                if page < 1 or page > int(poke_count/20)+1:
                    page = 1

            t = Translator(ctx.guild.id, loadStrings = True)

            closedView = pokeView(90)
            openedView = pokeView(90)
            pokedex = Pokedex(ctx.guild.id, user, page-1)

            open = discord.ui.Button(label = "Open", emoji = "🌐")
            async def openCallback(interaction: discord.Interaction):
                nonlocal openedView, pokedex
                pokedex.open()
                await interaction.message.edit(embed = pokedex.embed, view = openedView)
                await interaction.response.defer()
            open.callback = openCallback


            shinies = discord.ui.Button(label = "Shinies", emoji = "✨")
            async def shiniesCallback(interaction: discord.Interaction):
                nonlocal openedView, pokedex
                pokedex.toggleShiny()
                pokedex.open()
                await interaction.message.edit(embed = pokedex.embed, view = openedView)
                await interaction.response.defer()
            shinies.callback = shiniesCallback



            close = discord.ui.Button(label = "Close", emoji = "🌐")
            async def closeCallback(interaction: discord.Interaction):
                nonlocal closedView, pokedex
                pokedex.close()
                await interaction.message.edit(embed = pokedex.embed, view = closedView)
                await interaction.response.defer()
            close.callback = closeCallback

            prev = discord.ui.Button(label = " ", emoji = "⬅️")
            async def prevCallback(interaction):
                nonlocal pokedex
                pokedex.prev()
                await interaction.message.edit(embed = pokedex.embed)
                await interaction.response.defer()
            prev.callback = prevCallback

            next = discord.ui.Button(label = " ", emoji = "➡️")
            async def nextCallback(interaction):
                nonlocal pokedex
                pokedex.next()
                await interaction.message.edit(embed = pokedex.embed)
                await interaction.response.defer()
            next.callback = nextCallback

            closedView.add_item(open)
            closedView.add_item(shinies)
            openedView.add_item(prev)
            openedView.add_item(close)
            openedView.add_item(next)


            message = await ctx.send(embed=pokedex.embed, view = closedView)
            closedView.setMessage(message)
            openedView.setMessage(message)
        else:
            content = t.getLocalString("commandBot", [])
            await ctx.send(content = content)


@bot.command(name="pokerank")
async def pokerank(ctx):
  if not ctx.author.bot :
    await ctx.channel.typing()

    def sort_on_pokemon(e):
        return e[0]

    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT COUNT(DISTINCT dex_id), user_id FROM poke_obtained GROUP BY user_id LIMIT 10")
    result = await cursor.fetchall()
    await close_conn(connection, cursor)
    result_list = []
    for i in range(len(result)):
        result_list.append([result[i][0], result[i][1]])
    result_list.sort(reverse=True, key=sort_on_pokemon)
    description = ""
    limit = 10
    i = 0
    ranking = 0
    while i != len(result_list) and ranking < 10:
        user = await bot.fetch_user(result_list[i][1])
        if user != None:
            ranking += 1;
            description += str(ranking) + "-" + user.name + " - " + str(result_list[i][0]) + "/" + str(poke_count) + "\n"
        i += 1
    embed=discord.Embed(title= "KannaSucre's Pokerank", colour=discord.Colour(0x635f))
    embed.set_thumbnail(url=bot.user.avatar)
    embed.add_field(name="Ranking :", value=description)
    await ctx.send(embed=embed)
