import random
from typing import Any

import discord

from src.resources.connection import closeStaticConn, getStaticReadingConn

# Init DB-dependent variables
connection, cursor = getStaticReadingConn()

cursor.execute("SELECT type_name, type_emoji_id from poke_type ORDER BY type_id")
tmp = cursor.fetchall()
TYPE_EMOJIS = [elem[1] for elem in tmp]

cursor.execute("SELECT COUNT(*) FROM poke_dex")
tmp = cursor.fetchone()
POKE_COUNT = tmp[0]

cursor.execute("SELECT COUNT(DISTINCT(link_type)) FROM poke_link")
tmp = cursor.fetchone()
NB_LINK_TYPES = tmp[0]

closeStaticConn(connection, cursor)


def set_add(target: set, value: Any):
    l = len(target)
    target.add(value)
    return len(target) != l


class Pokemon:
    def __init__(self, bot, interaction: discord.Interaction, linkType: int, pokeID: int):
        self.bot = bot
        self.interaction = interaction
        self.linkType = linkType

        if pokeID < 1 or pokeID > POKE_COUNT:
            raise ValueError(f"Poke_id must be between 0 and {POKE_COUNT}.")

        self.id = pokeID
        self.shiny = False
        self.currentLink = 0
        self._fetch_details()
        self._update_from_current_link()

    def _fetch_details(self, form_alt: int = None, form_sex: str = None):
        conn, cursor = getStaticReadingConn()
        cursor.execute(
            """SELECT dex_id, form_alt, form_sex, link_normal, link_shiny, form_label, form_type1, form_type2, evo_pre, evo_pre_alt, evo_method from poke_link
            JOIN poke_form USING(dex_id, form_alt, form_sex)
            JOIN poke_dex USING(dex_id)
			LEFT JOIN poke_evolution ON evo_post = dex_id and evo_post_alt = form_alt
            WHERE dex_id = %s and link_type = %s
            ORDER BY form_alt, form_sex
        """
            % (self.id, self.linkType)
        )
        self.alts = cursor.fetchall()
        closeStaticConn(conn, cursor)

        self.currentLink = 0
        if form_alt is not None:
            for i in range(0, len(self.alts)):
                row = self.alts[i]

                if row[1] == form_alt and (form_sex is None or row[2] == form_sex):
                    self.currentLink = i
                    return

            raise ValueError(
                f"No such alt ({form_alt}), genre ({form_sex}) for Pokemon n°{self.id}"
            )

    def _update_from_current_link(self):
        current_data = self.alts[self.currentLink]

        self.id = current_data[0]
        self.alt = current_data[1]
        self.genre = current_data[2]
        self.link_normal = current_data[3]
        self.link_shiny = current_data[4]
        self.label = current_data[5]
        self.type1 = current_data[6]
        self.type2 = current_data[7]
        self.method = current_data[10]

        self.name = self.bot.translator.getLocalPokeString(self.interaction, "name" + str(self.id))
        self.description = self.bot.translator.getLocalPokeString(
            self.interaction, "desc" + str(self.id)
        )

        if self.genre == "f":
            self.name += "\u2640"
        if self.genre == "m":
            self.name += "\u2642"

        connection, cursor = getStaticReadingConn()
        cursor.execute(
            "SELECT evo_post, evo_post_alt, form_label FROM poke_evolution JOIN poke_form ON evo_post = poke_form.dex_id AND evo_post_alt = form_alt WHERE evo_pre = %s and evo_pre_alt = %s"
            % (self.id, self.alt)
        )
        self.evolutions = cursor.fetchall()
        s = set()
        filtered_evolutions = []
        for row in self.evolutions:
            if set_add(s, f"{row[0]}-{row[1]}"):
                filtered_evolutions.append(row)

        self.evolutions = filtered_evolutions
        closeStaticConn(connection, cursor)

    def next_alt(self):
        self.currentLink = (self.currentLink + 1) % len(self.alts)
        self._update_from_current_link()

    def prev_alt(self):
        self.currentLink = (self.currentLink - 1) % len(self.alts)
        self._update_from_current_link()

    def switchType(self):
        self.linkType = (self.linkType + 1) % NB_LINK_TYPES
        alt = self.alts[self.currentLink][1]
        genre = self.alts[self.currentLink][2]

        self._fetch_details(alt, genre)
        self._update_from_current_link()

    def devolve(self):
        if self.alts[self.currentLink][8] is not None:
            self.id = self.alts[self.currentLink][8]
            self._fetch_details(self.alts[self.currentLink][9])
            self._update_from_current_link()
            return True
        return False

    def evolve(self, evolution: int = 0):
        self.id = self.evolutions[evolution][0]
        self.alt = self.evolutions[evolution][1]
        self._fetch_details(self.alt)
        self._update_from_current_link()

    def toggleShiny(self):
        self.shiny = not self.shiny

    def getLink(self):
        return self.link_shiny if self.shiny else self.link_normal

    def getEvolutions(self):
        return self.evolutions

    def get_pokeinfo_embed(self):
        formString = self.bot.translator.getLocalString(
            self.interaction, "pokeForm", [("form", self.label)]
        )

        # Title and image
        e = discord.Embed(
            title="N°" + str(self.id) + " : " + self.name + (":sparkles:" if self.shiny else ""),
            description=formString,
        )
        e.set_image(url=self.link_shiny if self.shiny else self.link_normal)

        # Description
        e.add_field(
            name=self.bot.translator.getLocalString(self.interaction, "description", []) + " :",
            value=self.description,
        )
        # Types
        types = f"{self.bot.translator.getLocalString(self.interaction, f'poketype{self.type1}', [])} <:poke_type:{TYPE_EMOJIS[self.type1]}>"
        if self.type2:
            types += f", {self.bot.translator.getLocalString(self.interaction, f'poketype{self.type2}', [])} <:poke_type:{TYPE_EMOJIS[self.type2]}>"
        e.add_field(
            name=self.bot.translator.getLocalString(self.interaction, "type", []) + " :",
            value=types,
            inline=False,
        )

        if self.method:
            evolved = self.bot.translator.getLocalString(self.interaction, "evolvedBy", [])
            field_name = self.bot.translator.getLocalString(self.interaction, "evolution", [])
            method = ""
            arguments = self.method.split()

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

            e.add_field(name=field_name + " :", value=evolved + " " + method, inline=False)
        text = self.bot.translator.getLocalString(
            self.interaction,
            "page",
            [("current", str(self.currentLink + 1)), ("total", str(len(self.alts)))],
        )
        e.set_footer(text=text)
        return e


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
            value=str(shiny[0]) + "/" + str(POKE_COUNT) + " shiny pokémons",
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

        self.page = (self.page) % (int(POKE_COUNT / 20) + 1)

        if Pokemons == []:
            list_pokemons = self.bot.translator.getLocalString(self.interaction, "noPoke", [])
        else:
            list_pokemons = ""
            list_index = 0
            while Pokemons[list_index][0] <= self.page * 20 and list_index != len(Pokemons) - 1:
                list_index += 1
            for i in range(self.page * 20, self.page * 20 + 20):
                if i < POKE_COUNT:
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
            description=str(number_of_pokemons) + "/" + str(POKE_COUNT) + " Pokémons",
        )
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokémons :", value=list_pokemons, inline=True)

        text = self.bot.translator.getLocalString(
            self.interaction,
            "page",
            [("current", str(self.page + 1)), ("total", str(int(POKE_COUNT / 20) + 1))],
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
            description=str(len(shinies)) + "/" + str(POKE_COUNT) + " " + shinyString,
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

        self.name = self.bot.translator.getLocalPokeString(self.interaction, "name" + str(self.id))

        if self.genre == "f":
            self.name += "\u2640"
        if self.genre == "m":
            self.name += "\u2642"

    def _get_shiny(self):
        self.shiny = True if random.randint(1, 256) == 1 else False

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
