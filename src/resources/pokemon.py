import random

import discord

from src.resources.connection import closeStaticConn, getStaticReadingConn

poke_count = 1010


connection, cursor = getStaticReadingConn()
cursor.execute("SELECT type_name, type_emoji_id from poke_type ORDER BY type_id")
tmp = cursor.fetchall()
closeStaticConn(connection, cursor)
type_emojis = [elem[1] for elem in tmp]


def get_current_link(bot, poke_id: int, poke_alt: int, poke_genre: str):
    connection, cursor = getStaticReadingConn()
    cursor.execute(
        "SELECT COUNT(*) FROM poke_form WHERE dex_id =? and form_alt <= ? and form_sex <= ?",
        (poke_id, poke_alt, poke_genre),
    )
    temp = cursor.fetchone()
    return temp[0]


def get_devolution(bot, poke_id: int, poke_alt: int):
    connection, cursor = getStaticReadingConn()
    cursor.execute(
        "SELECT evo_pre, evo_pre_alt, evo_method FROM poke_evolution WHERE evo_post = ? AND evo_post_alt = ?",
        (poke_id, poke_alt),
    )
    temp = cursor.fetchone()
    return None if temp == [] else temp


def get_evolutions(bot, poke_id: int, poke_alt: int):
    connection, cursor = getStaticReadingConn()
    cursor.execute(
        "SELECT DISTINCT evo_post, evo_post_alt, dex_name, form_label  FROM poke_evolution JOIN poke_dex ON evo_post = poke_dex.dex_id JOIN poke_form ON evo_post = poke_form.dex_id and evo_post_alt = form_alt WHERE evo_pre = ? and evo_pre_alt = ?",
        (poke_id, poke_alt),
    )
    temp = cursor.fetchall()
    if temp == []:
        return None
    else:
        evolutions = []
        uniques = []
        for evo in temp:
            checkUnique = str(evo[0]) + "." + str(evo[1])
            if checkUnique not in uniques:
                uniques.append(checkUnique)
                evolutions.append(evo)
        return evolutions


class Pokemon:
    def __init__(self, bot, interaction: discord.Interaction, linkType: int, pokeID: int):
        self.bot = bot
        self.interaction = interaction
        self.linkType = linkType

        if pokeID <= poke_count and pokeID > 0:
            self.id = pokeID
            self.shiny = False
            self.current_link = 1
            self.alt = 0
            self.update_properties()

        else:
            raise ValueError(f"Poke_id must be between 0 and {poke_count}.")

    def update_properties(self):
        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT link_normal, link_shiny, form_sex, form_label, form_type1, form_type2 FROM poke_dex JOIN poke_form USING(dex_id) JOIN poke_link USING(dex_id, form_alt, form_sex) WHERE dex_id = ? AND form_alt = ? AND link_type = ?",
            (self.id, self.alt, self.linkType),
        )
        temp = cursor.fetchone()

        self.name = self.bot.translator.getLocalPokeString(self.interaction, "name" + str(self.id))
        self.description = self.bot.translator.getLocalPokeString(
            self.interaction, "desc" + str(self.id)
        )
        self.link = temp[0]
        self.shiny_link = temp[1]
        self.genre = temp[2]
        self.label = temp[3]
        self.type1 = temp[4]
        self.type2 = temp[5]

        cursor.execute("SELECT * FROM poke_form WHERE dex_id = ?", (self.id,))
        self.pokelinks = cursor.fetchall()
        self.pokelinks = self.pokelinks[0]
        cursor.execute("SELECT MAX(form_alt) FROM poke_form WHERE dex_id = ?", (self.id,))
        self.pokealts = cursor.fetchone()
        self.pokealts = self.pokealts[0]
        self.devolution = get_devolution(self.bot, self.id, self.alt)
        self.evolutions = get_evolutions(self.bot, self.id, self.alt)
        closeStaticConn(connection, cursor)

    def next_alt(self):
        if self.pokelinks > 1:
            connection, cursor = getStaticReadingConn()
            nextAlt = False
            if self.genre == "f":
                try:
                    self.genre = "m"
                    cursor.execute(
                        "SELECT link_normal, link_shiny, form_label FROM poke_form JOIN poke_link USING(dex_id, form_alt, form_sex) WHERE dex_id = ? AND form_alt = ? AND form_sex = ? AND link_type = ?",
                        (self.id, self.alt, self.genre, self.linkType),
                    )
                    temp = cursor.fetchone()
                    self.link = temp[0]
                    self.shiny_link = temp[1]
                    self.label = temp[2]

                except TypeError:
                    nextAlt = True
                    pass
            else:
                nextAlt = True

            if nextAlt:
                if self.alt != self.pokealts:
                    self.alt += 1
                else:
                    self.alt = 0
                cursor.execute(
                    "SELECT link_normal, link_shiny, form_sex, form_label FROM poke_form JOIN poke_link USING(dex_id, form_alt, form_sex) WHERE dex_id = ? AND form_alt = ? AND link_type = ?",
                    (self.id, self.alt, self.linkType),
                )
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.genre = temp[2]
                self.label = temp[3]
            self.evolutions = get_evolutions(self.bot, self.id, self.alt)
            self.devolution = get_devolution(self.bot, self.id, self.alt)
            self.current_link = get_current_link(self.bot, self.id, self.alt, self.genre)
            closeStaticConn(connection, cursor)

    def prev_alt(self):
        if self.pokelinks > 1:
            connection, cursor = getStaticReadingConn()
            nextAlt = False
            if self.genre == "m":
                try:
                    self.genre = "f"
                    cursor.execute(
                        "SELECT link_normal, link_shiny, form_label FROM poke_form JOIN poke_link USING(dex_id, form_alt, form_sex) JOIN poke_type WHERE dex_id = ? AND form_alt = ? AND form_sex = ? AND link_type = ?",
                        (self.id, self.alt, self.genre, self.linkType),
                    )
                    temp = cursor.fetchone()
                    self.link = temp[0]
                    self.shiny_link = temp[1]
                    self.label = temp[2]

                except TypeError:
                    prev_alt = True
                    pass
            else:
                prev_alt = True

            if prev_alt:
                if self.alt != 0:
                    self.alt -= 1
                else:
                    self.alt = self.pokealts
                cursor.execute(
                    "SELECT link_normal, link_shiny, form_sex, form_label FROM poke_form JOIN poke_link USING(dex_id, form_alt, form_sex) WHERE dex_id = ? AND form_alt = ? AND link_type = ? ORDER BY form_sex DESC",
                    (self.id, self.alt, self.linkType),
                )
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.genre = temp[2]
                self.label = temp[3]
            self.devolution = get_devolution(self.bot, self.id, self.alt)
            self.evolutions = get_evolutions(self.bot, self.id, self.alt)
            self.current_link = get_current_link(self.bot, self.id, self.alt, self.genre)
            closeStaticConn(connection, cursor)

    def get_pokeinfo_embed(self):
        poke_sex = ""
        if self.genre == "f":
            poke_sex += "\u2640"
        if self.genre == "m":
            poke_sex += "\u2642"

        formString = self.bot.translator.getLocalString(
            self.interaction, "pokeForm", [("form", self.label)]
        )
        if self.shiny:
            e = discord.Embed(
                title="N°" + str(self.id) + " : " + self.name + poke_sex + ":sparkles: ",
                description=formString,
            )
            e.set_image(url=self.shiny_link)
        else:
            e = discord.Embed(
                title="N°" + str(self.id) + " : " + self.name + poke_sex,
                description=formString,
            )
            e.set_image(url=self.link)

        e.add_field(
            name=self.bot.translator.getLocalString(self.interaction, "description", []) + " :",
            value=self.description,
        )
        types = f"{self.bot.translator.getLocalString(self.interaction, f'poketype{self.type1}', [])} <:poke_type:{type_emojis[self.type1]}>"
        if self.type2:
            types += f", {self.bot.translator.getLocalString(self.interaction, f'poketype{self.type2}', [])} <:poke_type:{type_emojis[self.type2]}>"
        e.add_field(
            name=self.bot.translator.getLocalString(self.interaction, "type", []) + " :",
            value=types,
            inline=False,
        )
        if self.devolution is not None:
            evolved = self.bot.translator.getLocalString(self.interaction, "evolvedBy", [])
            name = self.bot.translator.getLocalString(self.interaction, "evolution", [])
            method = ""
            arguments = self.devolution[2].split()

            if arguments[0] == "friend" or arguments[0] == "trade" or arguments[0][:4] == "spec":
                method = self.bot.translator.getLocalPokeEvo(self.interaction, arguments[0], {})
            elif arguments[0] == "item":
                item = self.bot.translator.getLocalPokeEvo(self.interaction, arguments[1], {})
                method = self.bot.translator.getLocalPokeEvo(
                    self.interaction, arguments[0], [("item", item)]
                )
            elif arguments[0] == "tradeItem":
                item = self.bot.translator.getLocalPokeEvo(self.interaction, arguments[1], {})
                method = self.bot.translator.getLocalPokeEvo(
                    self.interaction, arguments[0], [("item", item)]
                )
            elif arguments[0] == "level":
                method = self.bot.translator.getLocalPokeEvo(
                    self.interaction, arguments[0], [("level", str(arguments[1]))]
                )

            if arguments[-1] == "Day" or arguments[-1] == "Night":
                method += " "
                method += self.bot.translator.getLocalPokeEvo(self.interaction, arguments[-1], [])

            method += "."

            e.add_field(name=name + " :", value=evolved + " " + method, inline=False)
        text = self.bot.translator.getLocalString(
            self.interaction,
            "page",
            [("current", str(self.current_link)), ("total", str(self.pokelinks))],
        )
        e.set_footer(text=text)
        return e

    def devolve(self):
        self.id = self.devolution[0]
        self.alt = self.devolution[1]
        self.update_properties()
        self.current_link = get_current_link(self.bot, self.id, self.alt, self.genre)

    def evolve(self, choice: int = 0):
        self.id = self.evolutions[choice][0]
        self.alt = self.evolutions[choice][1]
        self.update_properties()
        self.current_link = get_current_link(self.bot, self.id, self.alt, self.genre)

    def switchType(self):
        self.linkType = (self.linkType + 1) % 2
        self.update_properties()


class Pokedex:
    def __init__(self, bot, interaction, user: discord.User, page: int = 0):
        self.bot = bot
        self.interaction = interaction
        self.page = page
        self.user = user
        self.shiny = False
        self.embed = self.__get_closed_pokedex()

    def next(self):
        self.page += 1
        if self.shiny:
            self.embed = self.__get_shiny_embed()
        else:
            self.embed = self.__get_pokedex_embed()

    def prev(self):
        self.page += -1
        if self.shiny:
            self.embed = self.__get_shiny_embed()
        else:
            self.embed = self.__get_pokedex_embed()

    def open(self):
        if self.shiny:
            self.embed = self.__get_shiny_embed()
        else:
            self.embed = self.__get_pokedex_embed()

    def close(self):
        self.shiny = False
        self.page = 0
        self.embed = self.__get_closed_pokedex()

    def toggleShiny(self):
        self.shiny = True

    def __get_closed_pokedex(self):
        connection, cursor = getStaticReadingConn()

        rarities = []

        rarities.append(self.bot.translator.getLocalString(self.interaction, "common", []))
        rarities.append(self.bot.translator.getLocalString(self.interaction, "uncommon", []))
        rarities.append(self.bot.translator.getLocalString(self.interaction, "rare", []))
        rarities.append(self.bot.translator.getLocalString(self.interaction, "superRare", []))
        rarities.append(self.bot.translator.getLocalString(self.interaction, "legendary", []))

        cursor.execute(
            "SELECT COUNT(distinct dex_id), dex_rarity FROM poke_obtained JOIN poke_dex USING(dex_id) WHERE user_id = ? GROUP BY dex_rarity ORDER BY dex_rarity",
            (self.user.id,),
        )
        obtained = cursor.fetchall()

        cursor.execute(
            "SELECT COUNT(*) FROM poke_obtained WHERE is_shiny = 1 AND user_id = ?",
            (self.user.id,),
        )
        shiny = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM poke_dex GROUP BY dex_rarity")
        totals = cursor.fetchall()
        closeStaticConn(connection, cursor)

        embed = discord.Embed(title=str(self.user.display_name) + "'s Pokedex")
        rarityCountStr = ""

        currentIndex = 0
        for i in range(5):
            if len(obtained) > currentIndex and obtained[currentIndex][1] == i + 1:
                rarityCountStr += (
                    "__"
                    + rarities[i]
                    + "__ :\n"
                    + str(obtained[currentIndex][0])
                    + "/"
                    + str(totals[i][0])
                    + " pokémons\n\n"
                )
                currentIndex += 1
            else:
                rarityCountStr += (
                    "__" + rarities[i] + "__ :\n0/" + str(totals[i][0]) + " pokémons\n\n"
                )

        embed.add_field(name="Pokémons : ", value=rarityCountStr)
        embed.add_field(
            name="Shinies✨ : ",
            value=str(shiny[0]) + "/" + str(poke_count) + " shiny pokémons",
            inline=False,
        )
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        return embed

    def __get_pokedex_embed(self):
        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT DISTINCT dex_id, dex_name, is_shiny FROM poke_dex JOIN poke_obtained USING(dex_id) WHERE user_id = ? ORDER BY dex_id;",
            (self.user.id,),
        )
        Pokemons = cursor.fetchall()
        cursor.execute(
            "SELECT COUNT(DISTINCT dex_id) FROM poke_obtained WHERE user_id = ?;",
            (self.user.id,),
        )
        number_of_pokemons = cursor.fetchone()
        number_of_pokemons = number_of_pokemons[0]

        closeStaticConn(connection, cursor)

        self.page = (self.page) % (int(poke_count / 20) + 1)

        if Pokemons == []:
            list_pokemons = self.bot.translator.getLocalString(self.interaction, "noPoke", [])
        else:
            list_pokemons = ""
            list_index = 0
            while Pokemons[list_index][0] <= self.page * 20 and list_index != len(Pokemons) - 1:
                list_index += 1
            for i in range(self.page * 20, self.page * 20 + 20):
                if i < poke_count:
                    if Pokemons[list_index][0] == i + 1:
                        pokeName = self.bot.translator.getLocalPokeString(
                            self.interaction, "name" + str(Pokemons[list_index][0])
                        )

                        if Pokemons[list_index][2]:
                            list_pokemons += str(i + 1) + " - " + pokeName + ":sparkles:\n"
                        else:
                            list_pokemons += str(i + 1) + " - " + pokeName + "\n"
                        if list_index < len(Pokemons) - 1:
                            list_index += 1
                    else:
                        list_pokemons += str(i + 1) + " - --------\n"
        title = self.bot.translator.getLocalString(
            self.interaction, "userPokedex", [("user", self.user.name)]
        )
        embed = discord.Embed(
            title=title,
            description=str(number_of_pokemons) + "/" + str(poke_count) + " Pokémons",
        )
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokémons :", value=list_pokemons, inline=True)

        text = self.bot.translator.getLocalString(
            self.interaction,
            "page",
            [("current", str(self.page + 1)), ("total", str(int(poke_count / 20) + 1))],
        )
        embed.set_footer(text=text)
        return embed

    def __get_shiny_embed(self):
        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT DISTINCT dex_id FROM poke_obtained JOIN poke_dex USING(dex_id) WHERE is_shiny = 1 AND user_id = ? ORDER BY dex_id",
            (self.user.id,),
        )
        shinies = cursor.fetchall()

        closeStaticConn(connection, cursor)

        self.page = (self.page) % (int(len(shinies) / 20) + 1)

        if shinies == []:
            list_pokemons = self.bot.translator.getLocalString(self.interaction, "noPoke", [])
        else:
            list_pokemons = ""
            list_index = 0

            count = 0
            for i in range(self.page * 20, (self.page + 1) * 20):
                if len(shinies) > self.page * 20 + count:
                    list_pokemons += (
                        str(shinies[i][0])
                        + " - "
                        + self.bot.translator.getLocalPokeString(
                            self.interaction, f"name{shinies[i][0]}"
                        )
                        + ":sparkles:\n"
                    )
                count += 1

        title = self.bot.translator.getLocalString(
            self.interaction, "userShiny", [("user", self.user.display_name)]
        )
        shinyString = self.bot.translator.getLocalString(self.interaction, "shinyPoke", [])
        embed = discord.Embed(
            title=title,
            description=str(len(shinies)) + "/" + str(poke_count) + " " + shinyString,
        )
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokémons :", value=list_pokemons, inline=True)
        text = self.bot.translator.getLocalString(
            self.interaction,
            "page",
            [
                ("current", str(self.page + 1)),
                ("total", str(int(len(shinies) / 20) + 1)),
            ],
        )
        embed.set_footer(text=text)
        return embed


class RandomPokemon:
    id: int
    name: str
    alt: int
    label: str
    genre: str
    rarity: int
    shiny: bool
    linktype: int
    link: str

    def __init__(self, bot, interaction, linkType: int):
        self.bot = bot
        self.linkType = linkType
        self.interaction = interaction

        self._get_rarity()
        self._get_shiny()
        self._fetch_pokemon_details()

        self.name = self.bot.translator.getLocalPokeString(interaction, "name" + str(self.id))

        if self.genre == "f":
            self.name += "\u2640"
        if self.genre == "m":
            self.name += "\u2642"

    def _get_shiny(self):
        self.shiny = True if random.randint(1, 256) == 1 else False
        self.shiny = True

    def _get_rarity(self):
        rand = random.randint(1, 100)
        if rand == 100:
            self.rarity = [
                5,
                self.bot.translator.getLocalString(self.interaction, "legendary", []),
            ]
        elif rand >= 95 and rand <= 99:
            self.rarity = [
                4,
                self.bot.translator.getLocalString(self.interaction, "superRare", []),
            ]
        elif rand >= 80 and rand <= 94:
            self.rarity = [3, self.bot.translator.getLocalString(self.interaction, "rare", [])]
        elif rand >= 55 and rand <= 79:
            self.rarity = [2, self.bot.translator.getLocalString(self.interaction, "uncommon", [])]
        else:
            self.rarity = [1, self.bot.translator.getLocalString(self.interaction, "common", [])]

    def _fetch_pokemon_details(self):
        connection, cursor = getStaticReadingConn()
        cursor.execute(
            """SELECT dex_id, form_alt, form_label, form_sex, link_normal, link_shiny from poke_link
            JOIN poke_form USING(dex_id, form_alt, form_sex)
            JOIN poke_dex USING(dex_id)
            WHERE dex_id = (SELECT dex_id FROM poke_dex WHERE dex_rarity = %s ORDER by RANDOM()) and link_type = %s
            ORDER BY RANDOM() LIMIT 1"""
            % (self.rarity[0], self.linkType),
        )
        temp = cursor.fetchone()
        closeStaticConn(connection, cursor)

        self.id = temp[0]
        self.alt = temp[1]
        self.label = temp[2]
        self.genre = temp[3]
        self.link = temp[5] if self.shiny else temp[4]
