from connection import *
from mentions import *
from prefix import *
from bot import *


sys.path.append("../ressources")


poke_count = 649


class slashPoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def get_rarity(self):
        rand = random.randint(1, 100)
        if rand == 100:
            return [5, "legendary"]
        elif rand >= 95 and rand <= 99:
            return [4, "Super Rare"]
        elif rand >= 80 and rand <=94:
            return [3, "Rare"]
        elif rand >= 55 and rand <=79:
            return [2, "Uncommon"]
        else:
            return [1, "Common"]



    def get_shiny(self):
        rand = random.randint(1, 256)
        if rand == 1:
            return True
        return False




    async def get_alt(self, poke_id):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT DISTINCT pokelink_alt FROM pokelink WHERE poke_id = ?", (poke_id, ))
        alt = await cursor.fetchall()
        await close_conn(connection, cursor)
        if len(alt) == 1:
            return alt[0][0]
        else:
            return alt[random.randint(0, len(alt)-1)][0]


    async def get_pokemon_sex(self, poke_id, poke_alt):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT pokelink_sex FROM pokelink WHERE poke_id = ? AND pokelink_alt = ?", (poke_id, poke_alt))
        data = await cursor.fetchall()
        await close_conn(connection, cursor)
        if len(data) == 1:
            return data[0][0]
        else:
            return data[random.randint(0,len(data)-1)][0]



    async def get_pokemon_id(self, rarity):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT poke_id, poke_name FROM pokedex WHERE poke_rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity, ))
        temp =    await cursor.fetchone()
        await close_conn(connection, cursor)
        return temp



    async def get_pokemon_details(self):
        rarity = self.get_rarity()
        poke_id = await self.get_pokemon_id(rarity[0])
        shiny = self.get_shiny()
        poke_alt = await self.get_alt(poke_id[0])
        poke_sex = await self.get_pokemon_sex(poke_id[0], poke_alt)
        connection, cursor = await get_conn("./files/ressources/bot.db")
        if shiny:
            await cursor.execute("SELECT pokelink_shiny FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
        else:
            await cursor.execute("SELECT pokelink_normal FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
        link = await cursor.fetchone()
        await close_conn(connection, cursor)
        return [poke_id[0], poke_id[1], rarity[0], rarity[1],poke_alt, shiny, poke_sex, link[0]]



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
                    await cursor.execute("UPDATE users SET user_last_roll_datetime = ? WHERE user_id = ?", (now, userID))
                await connection.commit()

                pokemon_details = await self.get_pokemon_details()

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon_details[0], pokemon_details[4] ))
                is_obtained = await cursor.fetchone()

                #Second chance
                if(is_obtained):
                        pokemon_details = await self.get_pokemon_details()

                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (userID, pokemon_details[0], pokemon_details[4] ))
                is_obtained = await cursor.fetchone()
                await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ?", (userID, pokemon_details[0]))
                is_pokedex = await cursor.fetchone()



                shiny_string = ""
                form_string = ""
                is_shiny = pokemon_details[5]

                if is_shiny:
                    shiny_string = "\nWait!! Is it shiny??? :sparkles:"
                if(is_obtained == None and (is_pokedex)):
                    form_string = "\nYou already had that Pokémon, but that's a new form! :new:"

                if is_obtained == None:
                    await cursor.execute("INSERT INTO pokemon_obtained (user_id, poke_id, pokelink_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (userID, pokemon_details[0], pokemon_details[4], int(is_shiny), now))
                    desc = "This is a **" + pokemon_details[3] + "** pokemon!" + form_string + shiny_string

                elif (is_obtained[3] == 0 and is_shiny):
                    await cursor.execute("UPDATE pokemon_obtained SET is_shiny = 1 WHERE user_id = ? and poke_id = ?", (userID, pokemon_details[0]))
                    desc = "This is a **" + pokemon_details[3] + "** pokemon!" + form_string + shiny_string
                else:
                    desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string + "\nYou already had that pokemon.:confused:\nRolls +" + str(0.25*pokemon_details[2]) + "."
                    await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon_details[2], userID))
                await connection.commit()
                e = discord.Embed(title = "Congratulation **" + str(userName) + "**, you got **" + pokemon_details[1] + "**!",    description = desc)
                e.set_image(url=pokemon_details[-1])
                await interaction.response.send_message(embed = e)
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



    async def get_pokeinfo_embed(self, poke_id, page, shiny):
        connection, cursor = await get_conn("./files/ressources/bot.db")
        await cursor.execute("SELECT poke_id, poke_name, pokelink_sex, pokelink_normal, pokelink_shiny, poke_desc, pokelink_label FROM pokelink JOIN pokedex USING(poke_id) WHERE poke_id = ?;", (poke_id, ))
        pokedetails = await cursor.fetchall()

        page = page % len(pokedetails)
        poke_sex = ""
        if(pokedetails[page][2] == "f"):
            poke_sex = "\u2640"
        if(pokedetails[page][2] == "m"):
            poke_sex = "\u2642"


        if(shiny):
            e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + ":sparkles: " + poke_sex, description = pokedetails[page][6] + " form")
            e.set_image(url=pokedetails[page][4])
        else:
            e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + poke_sex, description = pokedetails[page][6] + " form")
            e.set_image(url=pokedetails[page][3])

        e.add_field(name = "Description : ", value=pokedetails[page][5])
        e.set_footer(text = "page " + str(page+1) + "/" + str(len(pokedetails)))
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
                        raise TypeError

                    await close_conn(connection, cursor)

                    page = 0
                    shiny = False
                    view = discord.ui.View()

                    async def prevCallback(interaction):
                        nonlocal page, shiny
                        page -= 1
                        await interaction.message.edit(embed = await self.get_pokeinfo_embed(poke_id, page, shiny), view = view)
                        await interaction.response.defer()
                    prev = discord.ui.Button(label = "Previous", style = discord.ButtonStyle.primary, emoji = "⬅️")
                    prev.callback = prevCallback

                    async def shinyCallback(interaction):
                        nonlocal page, shiny
                        shiny = not shiny
                        await interaction.message.edit(embed = await self.get_pokeinfo_embed(poke_id, page, shiny), view = view)
                        await interaction.response.defer()
                    shinyButton = discord.ui.Button(label = "Shiny", style = discord.ButtonStyle.secondary, emoji = "✨")
                    shinyButton.callback = shinyCallback

                    async def nextCallback(interaction):
                        nonlocal page, shiny
                        page += 1
                        await interaction.message.edit(embed = await self.get_pokeinfo_embed(poke_id, page, shiny), view = view)
                        await interaction.response.defer()
                    next = discord.ui.Button(label = "Next", style = discord.ButtonStyle.primary, emoji = "➡️")
                    next.callback = nextCallback

                    view.add_item(prev)
                    view.add_item(shinyButton)
                    view.add_item(next)

                    await interaction.response.send_message(embed = await self.get_pokeinfo_embed(poke_id, 0, False), view=view)

                except TypeError:
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


    async def get_pokedex_embed(self, user, page):
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
