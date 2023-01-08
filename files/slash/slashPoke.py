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
            await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM dis_user WHERE user_id =?", (userID, ))
            data = await cursor.fetchone()

            last_roll = data[0]
            pity = data[1]
            now = time.time()
            time_since = int(now - last_roll)

            if time_since > 7200 or pity >= 1:
                if time_since < 7200:
                    pity -= 1
                    await cursor.execute("UPDATE dis_user SET user_pity = ? WHERE user_id = ?", (pity, userID))
                else:
                    await cursor.execute("UPDATE dis_user SET user_last_roll_datetime = ? WHERE user_id = ?", (now, userID))
                await connection.commit()

                pokemon = Pokemon(interaction = interaction)

                await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()

                #Second chance
                if(is_obtained):
                        pokemon = Pokemon(interaction = interaction)

                await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ? AND form_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()
                await cursor.execute("SELECT * FROM poke_obtained WHERE user_id = ? AND dex_id = ?", (userID, pokemon.id))
                is_pokedex = await cursor.fetchone()



                shiny_string = ""
                form_string = ""
                link = pokemon.link


                pokeRarity = bot.translator.getLocalString(interaction, "pokeRarity", [("rarity", pokemon.rarity[1])])
                if pokemon.shiny:
                    shiny_string = "\n"
                    shiny_string += bot.translator.getLocalString(interaction, "isShiny", [])

                #New Form
                if(is_obtained == None and (is_pokedex)):
                    form_string = "\n"
                    form_string += bot.translator.getLocalString(interaction, "pokeNewForm", [])

                #New Pokémon
                if is_obtained == None:
                    await cursor.execute("INSERT INTO poke_obtained (user_id, dex_id, form_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (userID, pokemon.id, pokemon.alt, int(pokemon.shiny), now))
                    desc = pokeRarity + form_string + shiny_string

                #Pokemon already captured but shiny
                elif (is_obtained[3] == 0 and pokemon.shiny):
                    await cursor.execute("UPDATE poke_obtained SET is_shiny = 1 WHERE user_id = ? and dex_id = ? and form_alt = ?", (userID, pokemon.id, pokemon.alt))
                    desc = pokeRarity + form_string + shiny_string

                #Pokemon already captured
                else:
                    pokeAlready = "\n"
                    pokeAlready += bot.translator.getLocalString(interaction, "pokeAlready", [])
                    pokeExtraRolls = bot.translator.getLocalString(interaction, "pokeExtraRolls", [("number", pokemon.rarity[0]*0.25)])
                    desc = pokeRarity + shiny_string + pokeAlready + "\n" +pokeExtraRolls
                    await cursor.execute("UPDATE dis_user SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon.rarity[0], userID))

                await connection.commit()
                title = bot.translator.getLocalString(interaction, "pokeCatch", [("user", userName), ("pokeName", pokemon.name)])
                e = discord.Embed(title = title, description = desc)
                e.set_image(url=link)
                await interaction.followup.send(content = link, embed = e)

            else:
                time_left = int(7200 - time_since)
                if time_left > 3600:
                    time_left -= 3600
                    time_left = int(time_left/60)
                    content = bot.translator.getLocalString(interaction, "rollsHours", [("user", userName), ("hours", 1), ("minutes", time_left), ("number", pity)])
                else:
                    time_left += 60
                    time_left = int(time_left/60)
                    content = bot.translator.getLocalString(interaction, "rollsMinutes", [("user", userName), ("minutes", time_left), ("number", pity)])
                await interaction.followup.send(content = content)
            await close_conn(connection, cursor)



    @app_commands.command(name = "pokeinfo", description = "Shows a pokemon's details!")
    @app_commands.describe(id="The pokemon's pokedex ID.", name="The pokemon's name.")
    async def pokeinfo(self, interaction: discord.Interaction, id: int = None, name: str = None):
        if not interaction.user.bot:
            if id is not None or name is not None:
                if name is not None:
                    poke_id = bot.translator.getPokeIdByName(interaction, name.lower())
                else:
                    poke_id = id

                #If poke_id is Illegal
                if poke_id > poke_count or poke_id <= 0 :
                    title = bot.translator.getLocalString(interaction, "pokeinfoNotFound", [])
                    description = bot.translator.getLocalString(interaction, "pokeinfoNoSuch", [])
                    e = discord.Embed(title = title, description = description)
                    await interaction.response.send_message(embed = e)
                    return


                pokemon = Pokemon(interaction = interaction, pokeID = poke_id)
                buttonView = pokeView(90)
                buttonView.setMessage(interaction)

            #Callback definition, and buttons generation
                label = bot.translator.getLocalString(interaction, "buttonEvolve", [])
                evolveButton = discord.ui.Button(label = label, style = discord.ButtonStyle.secondary, emoji = "⏫", row = 1)
                prev = discord.ui.Button(label = " ", style = discord.ButtonStyle.primary, emoji = "⬅️", row = 2)
                label = bot.translator.getLocalString(interaction, "buttonShiny", [])
                shinyButton = discord.ui.Button(label = label, style = discord.ButtonStyle.secondary, emoji = "✨", row = 2)
                next = discord.ui.Button(label = " ", style = discord.ButtonStyle.primary, emoji = "➡️", row = 2)
                label = bot.translator.getLocalString(interaction, "buttonDevolve", [])
                devolveButton = discord.ui.Button(label = label, style = discord.ButtonStyle.secondary, emoji = "⏬", row = 3)

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
                            dropdown = PokeDropdown(interaction, pokemon, buttonView)

                            evoView = pokeView(90)
                            evoView.setMessage(buttonView.message)
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

            else:
                content = bot.translator.getLocalString(interaction, "pokeinfoInput", [])
                await interaction.response.send_message(content = content)


    @app_commands.command(name = "rolls", description = "Displays how much pokerolls you have, and when your next free roll will be.")
    async def rolls(self, interaction: discord.Interaction):

        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM dis_user WHERE user_id =?", (interaction.user.id, ))
        data = await cursor.fetchone()
        last_roll = data[0]
        pity = data[1]
        now = time.time()
        time_since = int(now - last_roll)
        time_left = int(7200 - time_since)
        userName = interaction.user.display_name
        if time_left <= 0:
            content = bot.translator.getLocalString(interaction, "rollsAvailable", [("user", userName), ("number", pity)])
            await interaction.response.send_message(content = content)
        elif time_left > 3600:
            time_left -= 3600
            time_left = int(time_left/60)
            content = bot.translator.getLocalString(interaction, "rollsHours", [("user", userName), ("hours", 1), ("minutes", time_left), ("number", pity)])
            await interaction.response.send_message(content = content)
        else:
            time_left += 60
            time_left = int(time_left/60)
            content = bot.translator.getLocalString(interaction, "rollsMinutes", [("user", userName), ("minutes", time_left), ("number", pity)])
            await interaction.response.send_message(content = content)
        await close_conn(connection, cursor)




    @app_commands.command(name = "pokedex", description = "Shows all the pokemons someone caught in their pokedex.")
    @app_commands.describe(user = "The user you want to see the pokedex of.", page="The pokedex's page you want to see.")
    async def pokedex(self, interaction: discord.Interaction, user: discord.User = None, page: int = 1):
        if not interaction.user.bot :
            if user is None:
                user = interaction.user
            if not user.bot:
                closedView = pokeView(90)
                closedView.setMessage(interaction)
                openedView = pokeView(90)
                openedView.setMessage(interaction)
                pokedex = Pokedex(interaction, user, page-1)

                label = bot.translator.getLocalString(interaction, "buttonOpen", [])
                open = discord.ui.Button(label = label, emoji = "🌐")
                async def openCallback(interaction):
                    nonlocal openedView, pokedex
                    pokedex.open()
                    await interaction.message.edit(embed = pokedex.embed, view = openedView)
                    await interaction.response.defer()
                open.callback = openCallback


                label = bot.translator.getLocalString(interaction, "buttonShinies", [])
                shinies = discord.ui.Button(label = label, emoji = "✨")
                async def shiniesCallback(interaction):
                    nonlocal openedView, pokedex
                    pokedex.toggleShiny()
                    pokedex.open()
                    await interaction.message.edit(embed = pokedex.embed, view = openedView)
                    await interaction.response.defer()
                shinies.callback = shiniesCallback


                label = bot.translator.getLocalString(interaction, "buttonClose", [])
                close = discord.ui.Button(label = label, emoji = "🌐")
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
                content = bot.translator.getLocalString(interaction, "commandBot", [])
                await interaction.response.send_message(content = content)

    @app_commands.command(name = "pokerank", description = "Displays the bot's top 10 best pokemon trainers!")
    async def pokerank(self, interaction: discord.Interaction):
        if not interaction.user.bot :

            await interaction.response.defer()

            connection, cursor = await get_conn("./files/ressources/bot.db")
            await cursor.execute("SELECT COUNT(DISTINCT dex_id) as nbPoke, user_name  FROM poke_obtained JOIN dis_user USING(user_id) GROUP BY user_id ORDER BY nbPoke desc limit 10")
            result = await cursor.fetchall()
            await close_conn(connection, cursor)
            result_list = []
            for i in range(len(result)):
                result_list.append([result[i][0], result[i][1]])
            description = ""
            i = 0
            limit = 10
            while i != len(result_list) and i < 10:
                description += str(i+1) + "- " + result_list[i][1] + " - " + str(result_list[i][0]) + "/" + str(poke_count) + "\n"
                i += 1;

            title = bot.translator.getLocalString(interaction, "pokerank", [])
            embed=discord.Embed(title = title, colour=discord.Colour(0x635f))
            embed.set_thumbnail(url=bot.user.avatar)
            name = bot.translator.getLocalString(interaction, "pokerankRanking", [])
            embed.add_field(name=name, value=description)
            await interaction.followup.send(embed=embed)
