from connection import *
from mentions import *
from pokemon import *
from prefix import *
from bot import *
from ui import *


sys.path.append("../ressources")


class slashPoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name ="poke", description="Catch a random pokémon!")
    async def poke(self, interaction: discord.Interaction):
        if not interaction.user.bot :

            userID = interaction.user.id
            userName = interaction.user.display_name

            #Not doidng it may cause bugs
            await interaction.response.defer()

            connection, cursor = await get_conn("./files/ressources/bot.db")
            await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (userID, ))
            data = await cursor.fetchone()

            last_roll = data[0]
            pity = data[1]
            now = time.time()
            time_since = int(now - last_roll)

            t = Translator(interaction.guild.id, loadStrings = True)
            if time_since > 7200 or pity >= 1:
                if time_since < 7200:
                    pity -= 1
                    await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity, userID))
                else:
                    await cursor.execute("UPDATE users SET user_last_roll_datetime = ? WHERE user_id = ?", (now, userID))
                await connection.commit()

                pokemon = Pokemon(guildID = interaction.guild.id)

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()

                #Second chance
                if(is_obtained):
                        pokemon = Pokemon(guildID = interaction.guild.id)

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()
                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ?", (userID, pokemon.id))
                is_pokedex = await cursor.fetchone()



                shiny_string = ""
                form_string = ""
                link = pokemon.link


                pokeRarity = t.getLocalString("pokeRarity", [("rarity", pokemon.rarity[1])])
                if pokemon.shiny:
                    shiny_string = "\n"
                    shiny_string += t.getLocalString("isShiny", [])
                    link = pokemon.shiny_link

                #New Form
                if(is_obtained == None and (is_pokedex)):
                    form_string = "\n"
                    form_string += t.getLocalString("pokeNewForm", [])

                #New Pokémon
                if is_obtained == None:
                    await cursor.execute("INSERT INTO pokemon_obtained (user_id, poke_id, pokelink_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (userID, pokemon.id, pokemon.alt, int(pokemon.shiny), now))
                    desc = pokeRarity + form_string + shiny_string

                #Pokemon already captured but shiny
                elif (is_obtained[3] == 0 and pokemon.shiny):
                    await cursor.execute("UPDATE pokemon_obtained SET is_shiny = 1 WHERE user_id = ? and poke_id = ?", (userID, pokemon.id))
                    desc = pokeRarity + form_string + shiny_string

                #Pokemon already captured
                else:
                    pokeAlready = "\n"
                    pokeAlready += t.getLocalString("pokeAlready", [])
                    pokeExtraRolls = t.getLocalString("pokeExtraRolls", [("number", pokemon.rarity[0]*0.25)])
                    desc = pokeRarity + shiny_string + pokeAlready + "\n" +pokeExtraRolls
                    await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon.rarity[0], userID))

                await connection.commit()
                title = t.getLocalString("pokeCatch", [("user", userName), ("pokeName", pokemon.name)])
                e = discord.Embed(title = title, description = desc)
                e.set_image(url=link)
                await interaction.followup.send(content = link, embed = e)

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
                await interaction.followup.send(content = content)
            await close_conn(connection, cursor)



    @app_commands.command(name = "pokeinfo", description = "Shows a pokemon's details!")
    @app_commands.describe(id="The pokemon's pokedex ID.", name="The pokemon's name.")
    async def pokeinfo(self, interaction: discord.Interaction, id: int = None, name: str = None):
        t = Translator(interaction.guild.id, loadStrings = True)

        if not interaction.user.bot:
            if id is not None or name is not None:
                connection, cursor = await get_conn("./files/ressources/bot.db")
                try:
                    if name is not None:
                        await cursor.execute("SELECT poke_id FROM pokedex WHERE lower(poke_name) = lower(?)", (name, ))
                        poke_id = await cursor.fetchone()
                        poke_id = poke_id[0]
                    else:
                        poke_id = id
                    if poke_id > poke_count or poke_id <= 0 :
                        await close_conn(connection, cursor)
                        raise TypeError


                    pokemon = Pokemon(guildID = interaction.guild.id, pokeID = poke_id)
                    buttonView = pokeView(interaction, 20)

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


                    async def prevCallback(interaction):
                        nonlocal pokemon
                        pokemon.prev_alt()
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                        await interaction.response.defer()
                    prev.callback = prevCallback


                    async def devolveCallback(interaction):
                        nonlocal pokemon
                        if pokemon.devolution is not None:
                            pokemon.devolve()
                            await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                        await interaction.response.defer()
                    devolveButton.callback = devolveCallback


                    async def shinyCallback(interaction):
                        nonlocal pokemon
                        pokemon.shiny = not pokemon.shiny
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                        await interaction.response.defer()
                    shinyButton.callback = shinyCallback


                    async def evolveCallback(interaction: discord.Interaction):
                        nonlocal pokemon, buttonView
                        await interaction.response.defer()
                        if pokemon.evolutions is not None:
                            if len(pokemon.evolutions) > 1:
                                dropdown = PokeDropdown(pokemon, buttonView)

                                evoView = pokeView(buttonView.interaction, 20)
                                evoView.add_item(dropdown)

                                await interaction.message.edit(view = evoView)
                            else:
                                pokemon.evolve()
                                await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed())
                    evolveButton.callback = evolveCallback



                    async def nextCallback(interaction):
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

                    await interaction.response.send_message(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = pokemon.get_pokeinfo_embed(), view = buttonView)


                except TypeError:
                    title = t.getLocalString("pokeinfoNotFound", [])
                    description = t.getLocalString("pokeinfoNoSuch", [])
                    e = discord.Embed(title = title, description = description)
                    await interaction.response.send_message(embed = e)
            else:
                content = t.getLocalString("pokeinfoInput", [])
                await interaction.response.send_message(content = content)


    @app_commands.command(name = "rolls", description = "Displays how much pokerolls you have, and when your next free roll will be.")
    async def rolls(self, interaction: discord.Interaction):
        t = Translator(interaction.guild.id, loadStrings = True)

        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (interaction.user.id, ))
        data = await cursor.fetchone()
        last_roll = data[0]
        pity = data[1]
        now = time.time()
        time_since = int(now - last_roll)
        time_left = int(7200 - time_since)
        userName = interaction.user.display_name
        if time_left <= 0:
            content = t.getLocalString("rollsAvailable", [("user", userName), ("number", pity)])
            await interaction.response.send_message(content = content)
        elif time_left > 3600:
            time_left -= 3600
            time_left = int(time_left/60)
            content = t.getLocalString("rollsHours", [("user", userName), ("hours", 1), ("minutes", time_left), ("number", pity)])
            await interaction.response.send_message(content = content)
        else:
            time_left += 60
            time_left = int(time_left/60)
            content = t.getLocalString("rollsMinutes", [("user", userName), ("minutes", time_left), ("number", pity)])
            await interaction.response.send_message(content = content)
        await close_conn(connection, cursor)




    @app_commands.command(name = "pokedex", description = "Shows all the pokemons someone caught in their pokedex.")
    @app_commands.describe(user = "The user you want to see the pokedex of.", page="The pokedex's page you want to see.")
    async def pokedex(self, interaction: discord.Interaction, user: discord.User = None, page: int = 1):
        if not interaction.user.bot :
            t = Translator(interaction.guild.id, loadStrings = True)

            if user is None:
                user = interaction.user
            if not user.bot:
                closedView = pokeView(interaction, 20)
                openedView = pokeView(interaction, 20)
                pokedex = Pokedex(user, page-1)

                open = discord.ui.Button(label = "Open", emoji = "🌐")
                async def openCallback(interaction):
                    nonlocal openedView, pokedex
                    pokedex.open()
                    await interaction.message.edit(embed = pokedex.embed, view = openedView)
                    await interaction.response.defer()
                open.callback = openCallback


                shinies = discord.ui.Button(label = "Shinies", emoji = "✨")
                async def shiniesCallback(interaction):
                    nonlocal openedView, pokedex
                    pokedex.toggleShiny()
                    pokedex.open()
                    await interaction.message.edit(embed = pokedex.embed, view = openedView)
                    await interaction.response.defer()
                shinies.callback = shiniesCallback



                close = discord.ui.Button(label = "Close", emoji = "🌐")
                async def closeCallback(interaction):
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


                await interaction.response.send_message(embed=pokedex.embed, view = closedView)
            else:
                content = t.getLocalString("commandBot", [])
                await interaction.response.send_message(content = content)

    @app_commands.command(name = "pokerank", description = "Displays the bot's top 10 best pokemon trainers!")
    async def pokerank(self, interaction: discord.Interaction):
        if not interaction.user.bot :

            def sort_on_pokemon(e):
                return e[0]

            await interaction.response.defer()

            connection, cursor = await get_conn("./files/ressources/bot.db")
            await cursor.execute("SELECT COUNT(DISTINCT poke_id), user_id FROM pokemon_obtained GROUP BY user_id LIMIT 10")
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
            await interaction.followup.send(embed=embed)
