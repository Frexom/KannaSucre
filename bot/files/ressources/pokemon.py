from connection import *
from bot import *

poke_count = 809




def get_rarity(guildID: int):
    t = Translator(guildID, loadStrings = True)
    rand = random.randint(1, 100)
    if rand == 100:
        return [5, t.getLocalString("legendary", [])]
    elif rand >= 95 and rand <= 99:
        return [4, t.getLocalString("superRare", [])]
    elif rand >= 80 and rand <=94:
        return [3, t.getLocalString("rare", [])]
    elif rand >= 55 and rand <=79:
        return [2, t.getLocalString("uncommon", [])]
    else:
        return [1, t.getLocalString("common", [])]



def get_shiny():
    rand = random.randint(1, 256)
    if rand == 1:
        return True
    return False

def get_pokemon_id(rarity: int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT poke_id FROM pokedex WHERE poke_rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity, ))
    temp = cursor.fetchone()
    close_static_conn(connection, cursor)
    return temp[0]

def get_pokemon_alt(poke_id:int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT DISTINCT pokelink_alt FROM pokelink WHERE poke_id = ?", (poke_id, ))
    alt = cursor.fetchall()
    close_static_conn(connection, cursor)
    if len(alt) == 1:
        return alt[0][0]
    else:
        return alt[random.randint(0, len(alt)-1)][0]

def get_pokemon_genre(poke_id: int, poke_alt: int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT pokelink_sex FROM pokelink WHERE poke_id = ? AND pokelink_alt = ?", (poke_id, poke_alt))
    data = cursor.fetchall()
    close_static_conn(connection, cursor)
    if len(data) == 1:
        return data[0][0]
    else:
        return data[random.randint(0,len(data)-1)][0]

def get_pokemon_link(poke_id:int, poke_alt:int, poke_genre:str, shiny:bool):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    if shiny:
        cursor.execute("SELECT pokelink_shiny FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id, poke_alt, poke_genre))
    else:
        cursor.execute("SELECT pokelink_normal FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id, poke_alt, poke_genre))
    temp = cursor.fetchone()
    close_static_conn(connection, cursor)
    return temp[0]

def get_current_link(poke_id: int, poke_alt: int, poke_genre: str):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT COUNT(*) FROM pokelink WHERE poke_id =? and pokelink_alt <= ? and pokelink_sex <= ?", (poke_id, poke_alt, poke_genre))
    temp = cursor.fetchone()
    return temp[0]

def get_devolution(poke_id : int, poke_alt:int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT evo_pre, evo_pre_alt, evo_method FROM evolutions WHERE evo_post = ? AND evo_post_alt = ?", (poke_id, poke_alt))
    temp = cursor.fetchone()
    return None if temp == [] else temp

def get_evolutions(poke_id: int, poke_alt: int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT DISTINCT evo_post, evo_post_alt, poke_name, pokelink_label  FROM evolutions JOIN pokedex ON evo_post = pokedex.poke_id JOIN pokelink ON evo_post = pokelink.poke_id and evo_post_alt = pokelink_alt WHERE evo_pre = ? and evo_pre_alt = ?", (poke_id, poke_alt))
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
    def __init__(self, guildID: int, pokeID: int = None):
        self.guildID = guildID
        self.translator = Translator(self.guildID, loadStrings = True, loadPoke = True)

        if pokeID is not None:
            if pokeID <= poke_count and pokeID > 0:
                self.id = pokeID
                self.shiny = False
                self.current_link = 1
                self.alt = 0
                self.update_properties()

            else:
                raise ValueError(f"Poke_id must be between 0 and {poke_count}.")
        else:
            self.rarity = get_rarity(guildID)
            self.shiny = get_shiny()
            self.id = get_pokemon_id(self.rarity[0])
            self.name = self.translator.getLocalPokeString("name"+str(self.id))
            self.alt = get_pokemon_alt(self.id)
            self.genre = get_pokemon_genre(self.id, self.alt)
            self.link = get_pokemon_link(self.id, self.alt, self.genre, self.shiny)

    def update_properties(self):
        connection, cursor = get_static_conn("./files/ressources/bot.db")
        cursor.execute("SELECT pokelink_normal, pokelink_shiny, pokelink_sex, pokelink_label FROM pokedex JOIN pokelink USING(poke_id) WHERE poke_id = ? AND pokelink_alt = ?", (self.id, self.alt))
        temp = cursor.fetchone()

        self.name = self.translator.getLocalPokeString("name"+str(self.id))
        self.description = self.translator.getLocalPokeString("desc"+str(self.id))
        self.link = temp[0]
        self.shiny_link = temp[1]
        self.genre = temp[2]
        self.label = temp[3]
        cursor.execute("SELECT COUNT(*) FROM pokelink WHERE poke_id = ?", (self.id, ))
        self.pokelinks = cursor.fetchone()
        self.pokelinks = self.pokelinks[0]
        cursor.execute("SELECT MAX(pokelink_alt) FROM pokelink WHERE poke_id = ?", (self.id, ))
        self.pokealts = cursor.fetchone()
        self.pokealts = self.pokealts[0]
        self.devolution = get_devolution(self.id, self.alt)
        self.evolutions = get_evolutions(self.id, self.alt)
        close_static_conn(connection, cursor)

    def next_alt(self):
        if self.pokelinks > 1:
            connection, cursor = get_static_conn("./files/ressources/bot.db")
            if self.genre == "f":
                self.genre = "m"
                cursor.execute("SELECT pokelink_normal, pokelink_shiny, pokelink_label FROM pokelink WHERE poke_id = ? AND pokelink_alt = ? AND pokelink_sex = ?", (self.id, self.alt, self.genre))
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.label = temp[2]
            else:
                if self.alt != self.pokealts:
                    self.alt += 1
                else:
                    self.alt = 0
                cursor.execute("SELECT pokelink_normal, pokelink_shiny, pokelink_sex, pokelink_label FROM pokelink WHERE poke_id = ? AND pokelink_alt = ?", (self.id, self.alt))
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.genre = temp[2]
                self.label = temp[3]
                self.devolution = get_devolution(self.id, self.alt)
            self.current_link = get_current_link(self.id, self.alt, self.genre)
            close_static_conn(connection, cursor)

    def prev_alt(self):
        if self.pokelinks > 1:
            connection, cursor = get_static_conn("./files/ressources/bot.db")
            if self.genre == "m":
                self.genre = "f"
                cursor.execute("SELECT pokelink_normal, pokelink_shiny, pokelink_label FROM pokelink WHERE poke_id = ? AND pokelink_alt = ? AND pokelink_sex = ?", (self.id, self.alt, self.genre))
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.label = temp[2]
            else:
                if self.alt != 0:
                    self.alt -= 1
                else:
                    self.alt = self.pokealts
                cursor.execute("SELECT pokelink_normal, pokelink_shiny, pokelink_sex, pokelink_label FROM pokelink WHERE poke_id = ? AND pokelink_alt = ? ORDER BY pokelink_sex DESC", (self.id, self.alt))
                temp = cursor.fetchone()
                self.link = temp[0]
                self.shiny_link = temp[1]
                self.genre = temp[2]
                self.label = temp[3]
                self.devolution = get_devolution(self.id, self.alt)
            self.current_link = get_current_link(self.id, self.alt, self.genre)
            close_static_conn(connection, cursor)

    def get_pokeinfo_embed(self):

        poke_sex = ""
        if(self.genre == "f"):
            poke_sex = "\u2640"
        if(self.genre == "m"):
            poke_sex = "\u2642"


        if(self.shiny):
            e = discord.Embed(title = "N°" + str(self.id) + " : " + self.name + ":sparkles: " + poke_sex, description = self.label + " form")
            e.set_image(url=self.shiny_link)
        else:
            e = discord.Embed(title = "N°" + str(self.id) + " : " + self.name + poke_sex, description = self.label + " form")
            e.set_image(url=self.link)

        e.add_field(name = self.translator.getLocalString("description", []) + " :", value=self.description)
        if(self.devolution is not None):
            value = self.translator.getLocalString("evolvedBy", [])
            name = self.translator.getLocalString("evolution", [])
            e.add_field(name = name + " :", value = value + self.devolution[2], inline=False)
        e.set_footer(text = "page " + str(self.current_link) + "/" + str(self.pokelinks))
        return e

    def devolve(self):
        self.id = self.devolution[0]
        self.alt = self.devolution[1]
        self.update_properties()
        self.current_link = get_current_link(self.id, self.alt, self.genre)

    def evolve(self, choice: int = 0):
        self.id = self.evolutions[choice][0]
        self.alt = self.evolutions[choice][1]
        self.update_properties()
        self.current_link = get_current_link(self.id, self.alt, self.genre)




class Pokedex():
    def __init__(self, user: discord.User, page: int = 0):
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
        connection, cursor = get_static_conn("./files/ressources/bot.db")

        rarities = ["Common", "Uncommon", "Rare", "Super rare", "Legendary"]

        cursor.execute("SELECT COUNT(distinct poke_id), poke_rarity FROM pokemon_obtained JOIN pokedex USING(poke_id) WHERE user_id = ? GROUP BY poke_rarity ORDER BY poke_rarity", (self.user.id,))
        obtained = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM pokemon_obtained WHERE is_shiny = 1 AND user_id = ?", (self.user.id,))
        shiny = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM pokedex GROUP BY poke_rarity")
        totals = cursor.fetchall()
        close_static_conn(connection, cursor)

        embed = discord.Embed(title = str(self.user.name) + "'s Pokedex")
        rarityCountStr = ""

        currentIndex = 0
        for i in range(5):
            if(len(obtained) > currentIndex and obtained[currentIndex][1] == i+1):
                rarityCountStr += "__" + rarities[i] + "__ :\n" + str(obtained[currentIndex][0]) + "/" + str(totals[i][0]) + " pokémons\n\n"
                currentIndex += 1
            else:
                rarityCountStr += "__" + rarities[i] + "__ :\n0/" + str(totals[i][0]) + " pokémons\n\n"

        embed.add_field(name = "Pokémons : ", value = rarityCountStr)
        embed.add_field(name = "Shinies✨ : ", value = str(shiny[0]) + "/" + str(poke_count) + " shiny pokémons", inline=False)
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        return embed

    def __get_pokedex_embed(self):

        connection, cursor = get_static_conn("./files/ressources/bot.db")
        cursor.execute("SELECT DISTINCT poke_id, poke_name, is_shiny FROM pokedex JOIN pokemon_obtained USING(poke_id) WHERE user_id = ? ORDER BY poke_id;", (self.user.id, ))
        Pokemons = cursor.fetchall()
        cursor.execute("SELECT COUNT(DISTINCT poke_id) FROM pokemon_obtained WHERE user_id = ?;", (self.user.id, ))
        number_of_pokemons = cursor.fetchone()
        number_of_pokemons = number_of_pokemons[0]

        close_static_conn(connection, cursor)

        self.page = (self.page) % (int(poke_count/20)+1)

        if Pokemons == [] :
            list_pokemons = "No pokemons."
        else:
            list_pokemons = ""
            list_index = 0
            while(Pokemons[list_index][0] <= self.page*20 and list_index != len(Pokemons)-1) :
                list_index += 1
            for i in range(self.page*20, self.page*20+20):
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
        embed=discord.Embed(title = str(self.user.name) + "'s Pokedex", description = str(number_of_pokemons) + "/" + str(poke_count) + " pokemons")
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokemons :", value=list_pokemons, inline=True)

        embed.set_footer(text = "page " + str(self.page+1) + "/" + str(int(poke_count/20)+1))
        return embed


    def __get_shiny_embed(self):
        connection, cursor = get_static_conn("./files/ressources/bot.db")
        cursor.execute("SELECT DISTINCT poke_id, poke_name FROM pokemon_obtained JOIN pokedex USING(poke_id) WHERE is_shiny = 1 AND user_id = ? ORDER BY poke_id", (self.user.id,))
        shinies = cursor.fetchall()

        close_static_conn(connection, cursor)

        self.page = (self.page) % (int(len(shinies)/20)+1)

        if shinies == []:
            list_pokemons = "No pokemons."
        else:
            list_pokemons = ""
            list_index = 0

            count = 0
            for i in range(self.page*20, (self.page+1)*20):
                if(len(shinies) > self.page*20 + count):

                    list_pokemons += str(shinies[i][0]) + " - " + shinies[i][1] + ":sparkles:\n"
                count += 1

        embed=discord.Embed(title = str(self.user.name) + "'s shiny Pokémons", description = str(len(shinies)) + "/" + str(poke_count) + " shiny pokemons")
        embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
        embed.add_field(name="Pokemons :", value=list_pokemons, inline=True)
        embed.set_footer(text = "page " + str(self.page+1) + "/" + str(int(len(shinies)/20)+1))
        return embed
