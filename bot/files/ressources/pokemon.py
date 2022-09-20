from connection import *
from bot import *

poke_count = 151


def get_rarity():
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

def get_shiny():
    rand = random.randint(1, 256)
    if rand == 1:
        return True
    return False

def get_pokemon_id(rarity: int):
    connection, cursor = get_static_conn("./files/ressources/bot.db")
    cursor.execute("SELECT poke_id, poke_name FROM pokedex WHERE poke_rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity, ))
    temp = cursor.fetchone()
    close_static_conn(connection, cursor)
    return temp

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
    return cursor.fetchone()


class Pokemon:
    def __init__(self, poke_id: int = None):
        if poke_id is not None:
            if poke_id < poke_count and poke_id > 0:
                self.id = poke_id
                self.shiny = False
                self.current_link = 1
                self.alt = 0
                self.update_properties()
            else:
                raise ValueError(f"Poke_id must be between 0 and {poke_count}.")
        else:
            self.rarity = get_rarity()
            self.shiny = get_shiny()
            self.id = get_pokemon_id(self.rarity[0])
            self.name = self.id[1]
            self.id = self.id[0]
            self.alt = get_pokemon_alt(self.id)
            self.genre = get_pokemon_genre(self.id, self.alt)
            self.link = get_pokemon_link(self.id, self.alt, self.genre, self.shiny)

    def update_properties(self):
        connection, cursor = get_static_conn("./files/ressources/bot.db")
        cursor.execute("SELECT poke_name, poke_desc, pokelink_normal, pokelink_shiny, pokelink_sex, pokelink_label FROM pokedex JOIN pokelink USING(poke_id) WHERE poke_id = ? AND pokelink_alt = ?", (self.id, self.alt))
        temp = cursor.fetchone()
        self.name = temp[0]
        self.description = temp[1]
        self.link = temp[2]
        self.shiny_link = temp[3]
        self.genre = temp[4]
        self.label = temp[5]
        cursor.execute("SELECT COUNT(*) FROM pokelink WHERE poke_id = ?", (self.id, ))
        self.pokelinks = cursor.fetchone()
        self.pokelinks = self.pokelinks[0]
        cursor.execute("SELECT MAX(pokelink_alt) FROM pokelink WHERE poke_id = ?", (self.id, ))
        self.pokealts = cursor.fetchone()
        self.pokealts = self.pokealts[0]
        self.devolution = get_devolution(self.id, self.alt)
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

    def devolve(self):
        self.id = self.devolution[0]
        self.alt = self.devolution[1]
        self.update_properties()
        self.current_link = get_current_link(self.id, self.alt, self.genre)
