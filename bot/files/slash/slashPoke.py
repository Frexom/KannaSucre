from connection import *
from mentions import *
from pokemon import *
from prefix import *
from bot import *


sys.path.append("../ressources")


#poke_count = 649
poke_count = 151

class slashPoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name ="poke", description="Catches a pokemon for you!")
    async def poke(self, interaction: discord.Interaction):
        if not interaction.user.bot :

            userID = interaction.user.id
            userName = interaction.user.display_name

            connection, cursor = await get_conn("./files/ressources/bot.db")
            await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (userID, ))
            data = await cursor.fetchone()
            last_roll = data[0]
            pity = data[1]
            now = time.time()
            time_since = int(now - last_roll)
            if time_since > 7200 or pity >= 1:
                if time_since < 7200:
                    pity -= 1
                    await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity, userID))
                else:
                    #await cursor.execute("UPDATE users SET user_last_roll_datetime = ? WHERE user_id = ?", (now, userID
                    pass
                await connection.commit()

                pokemon = Pokemon()

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()

                #Second chance
                if(is_obtained):
                        pokemon = Pokemon()

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon.id, pokemon.alt ))
                is_obtained = await cursor.fetchone()
                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ?", (userID, pokemon.id))
                is_pokedex = await cursor.fetchone()



                shiny_string = ""
                form_string = ""
                link = pokemon.link

                if pokemon.shiny:
                    shiny_string = "\nWait!! Is it shiny??? :sparkles:"
                    link = pokemon.shiny_link

                if(is_obtained == None and (is_pokedex)):
                    form_string = "\nYou already had that Pokémon, but that's a new form! :new:"

                if is_obtained == None:
                    await cursor.execute("INSERT INTO pokemon_obtained (user_id, poke_id, pokelink_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (userID, pokemon.id, pokemon.alt, int(pokemon.shiny), now))
                    desc = "This is a **" + pokemon.rarity[1] + "** pokemon!" + form_string + shiny_string

                elif (is_obtained[3] == 0 and pokemon.shiny):
                    await cursor.execute("UPDATE pokemon_obtained SET is_shiny = 1 WHERE user_id = ? and poke_id = ?", (userID, pokemon.id))
                    desc = "This is a **" + pokemon.rarity[1] + "** pokemon!" + form_string + shiny_string
                else:
                    desc = "This is a **" + pokemon.rarity[1] + "** pokemon!" + shiny_string + "\nYou already had that pokemon.:confused:\nRolls +" + str(0.25*pokemon.rarity[0]) + "."
                    await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon.rarity[0], userID))
                await connection.commit()
                e = discord.Embed(title = "Congratulation **" + str(userName) + "**, you got **" + pokemon.name + "**!",    description = desc)
                e.set_image(url=link)
                await interaction.response.send_message(content = link, embed = e)
            else:
                time_left = int(7200 - time_since)
                if time_left > 3600:
                    time_left -= 3600
                    time_left = int(time_left/60)
                    await interaction.response.send_message(str(userName) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
                else:
                    time_left += 60
                    time_left = int(time_left/60)
                    await interaction.response.send_message(str(userName) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
            await close_conn(connection, cursor)



    async def get_pokeinfo_embed(self, pokemon):

        poke_sex = ""
        if(pokemon.genre == "f"):
            poke_sex = "\u2640"
        if(pokemon.genre == "m"):
            poke_sex = "\u2642"


        if(pokemon.shiny):
            e = discord.Embed(title = "N°" + str(pokemon.id) + " : " + pokemon.name + ":sparkles: " + poke_sex, description = pokemon.label + " form")
            e.set_image(url=pokemon.shiny_link)
            e.set_footer(text=pokemon.shiny_link + " | page " + str(pokemon.current_link) + "/" + str(pokemon.pokelinks))
        else:
            e = discord.Embed(title = "N°" + str(pokemon.id) + " : " + pokemon.name + poke_sex, description = pokemon.label + " form")
            e.set_image(url=pokemon.link)
            e.set_footer(text=pokemon.link + " | page " + str(pokemon.current_link) + "/" + str(pokemon.pokelinks))

        e.add_field(name = "Description : ", value=pokemon.description)
        if(pokemon.devolution is not None):
            e.add_field(name = "Evolution : ", value = "Has evolved by " + pokemon.devolution[2], inline=False)
        e.set_footer(text = "page " + str(pokemon.current_link) + "/" + str(pokemon.pokelinks))
        return e




    @app_commands.command(name = "pokeinfo", description = "Shows a pokemon's details!")
    @app_commands.describe(id="The pokemon's pokedex ID.", name="The pokemon's name.")
    async def pokeinfo(self, interaction: discord.Interaction, id: int = None, name: str = None):
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


                    pokemon = Pokemon(poke_id)
                    view = discord.ui.View()

                #Callback definition, and buttons generation
                    prev = discord.ui.Button(label = "Previous", style = discord.ButtonStyle.primary, emoji = "⬅️")
                    async def prevCallback(interaction):
                        nonlocal pokemon
                        pokemon.prev_alt()
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = await self.get_pokeinfo_embed(pokemon), view = view)
                        await interaction.response.defer()
                    prev.callback = prevCallback


                    devolveButton = discord.ui.Button(label = "Devolve", style = discord.ButtonStyle.secondary, emoji = "⏬")
                    async def devolveCallback(interaction):
                        nonlocal pokemon, view, devolveButton
                        pokemon.devolve()
                        if pokemon.devolution is None:
                            view.remove_item(devolveButton)
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = await self.get_pokeinfo_embed(pokemon), view = view)
                        await interaction.response.defer()
                    devolveButton.callback = devolveCallback


                    shinyButton = discord.ui.Button(label = "Shiny", style = discord.ButtonStyle.secondary, emoji = "✨")
                    async def shinyCallback(interaction):
                        nonlocal pokemon
                        pokemon.shiny = not pokemon.shiny
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = await self.get_pokeinfo_embed(pokemon), view = view)
                        await interaction.response.defer()
                    shinyButton.callback = shinyCallback


                    next = discord.ui.Button(label = "Next", style = discord.ButtonStyle.primary, emoji = "➡️")
                    async def nextCallback(interaction):
                        nonlocal pokemon
                        pokemon.next_alt()
                        await interaction.message.edit(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = await self.get_pokeinfo_embed(pokemon), view = view)
                        await interaction.response.defer()
                    next.callback = nextCallback


                    view.add_item(prev)
                    if(pokemon.devolution is not None):
                        view.add_item(devolveButton)
                    view.add_item(shinyButton)
                    view.add_item(next)

                    await interaction.response.send_message(content = pokemon.shiny_link if pokemon.shiny else pokemon.link, embed = await self.get_pokeinfo_embed(pokemon), view=view)

                except TimeoutError:
                    e = discord.Embed(title = "Not found :(", description = "No such pokemon")
                    await interaction.response.send_message(embed = e)
            else:
                await interaction.response.send_message("Please input either the Pokémon's ID or name.")
        else:
            await interaction.response.send_message("This command isn't supported for bots.")

    @app_commands.command(name="rolls", description = "Displays how much pokerolls you have, and when your next free roll will be.")
    async def rolls(self, interaction: discord.Interaction):
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
            await interaction.response.send_message(str(userName) + ", your poke roll is available.\nRolls : `" + str(pity)+ "`.")
        elif time_left > 3600:
            time_left -= 3600
            time_left = int(time_left/60)
            await interaction.response.send_message(str(userName) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
        else:
            time_left += 60
            time_left = int(time_left/60)
            await interaction.response.send_message(str(userName) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
        await close_conn(connection, cursor)


    async def get_pokedex_embed(self, user : discord.Member, page : int):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT DISTINCT poke_id, poke_name, is_shiny FROM pokedex JOIN pokemon_obtained USING(poke_id) WHERE user_id = ? ORDER BY poke_id;", (user.id, ))
        Pokemons = await cursor.fetchall()
        await cursor.execute("SELECT COUNT(DISTINCT poke_id) FROM pokemon_obtained WHERE user_id = ?;", (user.id, ))
        number_of_pokemons = await cursor.fetchone()
        number_of_pokemons = number_of_pokemons[0]
        if Pokemons == [] :
            list_pokemons = "No pokemons."
        else:
            list_pokemons = ""
            list_index = 0
            while(Pokemons[list_index][0] <= page*20 and list_index != len(Pokemons)-1) :
                list_index += 1
            for i in range(page*20, page*20+20):
                if i < poke_count:
                    if Pokemons[list_index][0] == i+1:
                        if Pokemons[list_index][2]:
                            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + ":sparkles:\n"
                        else:
                            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + "\n"
                        if list_index < len(Pokemons)-1:
                            list_index += 1
                    else:
                        list_pokemons += str(i+1) + " - --------\n"
        embed=discord.Embed(title = str(user.name) + "'s Pokedex", description = str(number_of_pokemons) + "/" + str(poke_count) + " pokemons")
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokemons :", value=list_pokemons, inline=True)
        embed.set_footer(text = "page " + str(page+1) + "/" + str(int(poke_count/20)+1))
        await close_conn(connection, cursor)
        return embed

    async def get_closed_pokedex(self, user: discord.Member):

        connection, cursor = await get_conn("./files/ressources/bot.db")

        rarities = ["Common", "Uncommon", "Rare", "Super rare", "Legendary"]

        await cursor.execute("SELECT COUNT(distinct poke_id) FROM pokemon_obtained JOIN pokedex USING(poke_id) WHERE user_id = ? GROUP BY poke_rarity", (user.id,))
        obtained = await cursor.fetchall()

        await cursor.execute("SELECT COUNT(*) FROM pokemon_obtained WHERE is_shiny = 1 AND user_id = ?", (user.id,))
        shiny = await cursor.fetchone()

        await cursor.execute("SELECT COUNT(*) FROM pokedex GROUP BY poke_rarity")
        totals = await cursor.fetchall()
        await close_conn(connection, cursor)

        embed = discord.Embed(title = str(user.name) + "'s Pokedex")
        rarityCountStr = ""
        for i in range(5):
            rarityCountStr += "__" + rarities[i] + "__ :\n" + str(obtained[i][0]) + "/" + str(totals[i][0]) + " pokémons\n\n"

        embed.add_field(name = "Pokémons : ", value = rarityCountStr)
        embed.add_field(name = "Shinies✨ : ", value = str(shiny[0]) + "/" + str(poke_count) + " shiny pokémons", inline=False)
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        return embed


    @app_commands.command(name = "pokedex", description = "Shows all the pokemons you caught in your pokedex.")
    @app_commands.describe(user = "The user you want to see the pokedex of.", page="The pokedex's page you want to see.")
    async def pokedex(self, interaction: discord.Interaction, user: discord.Member = None, page: int = 1):
        if not interaction.user.bot :
            if user is None:
                user = interaction.user
            if not user.bot:
                closedView = discord.ui.View()
                openedView = discord.ui.View()
                page = page-1

                async def openCallback(interaction):
                    nonlocal user, page, openedView
                    await interaction.message.edit(embed = await self.get_pokedex_embed(user, page), view = openedView)
                    await interaction.response.defer()
                open = discord.ui.Button(label = "Open", emoji = "🌐")
                open.callback = openCallback

                async def prevCallback(interaction):
                    nonlocal page, user
                    page = (page - 1) % (int(poke_count/20)+1)
                    await interaction.message.edit(embed = await self.get_pokedex_embed(user, page))
                    await interaction.response.defer()
                prev = discord.ui.Button(label = "Previous", emoji = "⬅️")
                prev.callback = prevCallback

                async def nextCallback(interaction):
                    nonlocal page, user
                    page = (page + 1) % (int(poke_count/20)+1)
                    await interaction.message.edit(embed = await self.get_pokedex_embed(user, page))
                    await interaction.response.defer()
                next = discord.ui.Button(label = "Next", emoji = "➡️")
                next.callback = nextCallback

                closedView.add_item(open)
                openedView.add_item(prev)
                openedView.add_item(next)


                await interaction.response.send_message(embed=await self.get_closed_pokedex(user), view = closedView)

            else:
                await interaction.response.send_message("This command isn't supported for bots.")
        else:
            await interaction.response.send_message("This command isn't supported for bots.")

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
