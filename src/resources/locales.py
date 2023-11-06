import csv
import os

from src.resources.adapter import ContextAdapter
from src.resources.connection import closeStaticConn, getStaticReadingConn


class Translator:
    def __init__(self):
        self.locales = {}
        self.strings = {}
        self.poke = {}
        self.evolutions = {}

        self.loadStrings()
        self.loadPoke()
        self.loadPokeEvos()

    def loadStrings(self):
        subfolders = [f.name for f in os.scandir("src/locales") if f.is_dir()]
        for folder in subfolders:
            file = "src/locales/{}/strings.csv".format(folder)
            with open(file, encoding="utf8") as f:
                reader = csv.reader(f, delimiter=",")
                self.strings[folder] = {rows[0]: rows[1] for rows in reader}

    def loadPoke(self):
        subfolders = [f.name for f in os.scandir("src/locales") if f.is_dir()]
        for folder in subfolders:
            file = "src/locales/{}/poke.csv".format(folder)
            with open(file, encoding="utf8") as f:
                reader = csv.reader(f, delimiter=",")
                self.poke[folder] = {rows[0]: rows[1] for rows in reader}

    def loadPokeEvos(self):
        subfolders = [f.name for f in os.scandir("src/locales") if f.is_dir()]
        for folder in subfolders:
            file = "src/locales/{}/evolutions.csv".format(folder)
            with open(file, encoding="utf8") as f:
                reader = csv.reader(f, delimiter=",")
                self.evolutions[folder] = {rows[0]: rows[1] for rows in reader}

    def getLocaleFromInteraction(self, interaction):
        id = None
        if isinstance(interaction, ContextAdapter):
            if interaction.getGuild() is not None:
                id = str(interaction.getGuild().id)

        elif interaction.guild is not None:
            id = str(interaction.guild.id)

        if id is not None:
            if id not in self.locales.keys():
                # Database query
                connection, cursor = getStaticReadingConn()
                cursor.execute("SELECT guild_locale FROM dis_guild WHERE guild_id = ?", (id,))
                locale = cursor.fetchone()
                closeStaticConn(connection, cursor)
                self.locales[id] = locale[0]
                return locale[0]
            else:
                return self.locales[id]
        else:
            return "en"

    def getLocalString(self, interaction, key: str, values: list):
        locale = self.getLocaleFromInteraction(interaction)
        string = self.strings[locale].get(key)

        if string is None:
            raise KeyError("String {} has not been found".format(key))

        for tuple in values:
            string = string.replace("{" + tuple[0] + "}", str(tuple[1]))
        string = string.replace("\\n", "\n")
        return string

    def getLocalPokeString(self, interaction, key: str):
        locale = self.getLocaleFromInteraction(interaction)
        string = self.poke[locale].get(key)

        if string is None:
            raise KeyError("String {} has not been found".format(key))
        else:
            return string

    def getLocalPokeEvo(self, interaction, key: str, values: list):
        locale = self.getLocaleFromInteraction(interaction)
        string = self.evolutions[locale].get(key)

        if string is None:
            raise KeyError("String {} has not been found".format(key))

        for tuple in values:
            string = string.replace("{" + tuple[0] + "}", str(tuple[1]))
        return string

    def getPokeIdByName(self, interaction, name: str):
        locale = self.getLocaleFromInteraction(interaction)
        name = name.lower()

        keys = [key for key, value in self.poke[locale].items() if value.lower() == name]
        if len(keys) == 1:
            return int(keys[0][4:])

        if locale != "en":
            keys = [key for key, value in self.poke["en"].items() if value.lower() == name]
            if len(keys) == 1:
                return int(keys[0][4:])
        return 0

    def updateCache(self, guildID, locale):
        self.locales[str(guildID)] = locale
