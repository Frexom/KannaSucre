import discord
import csv
import os

from adapter import *
from connection import *


class Translator():
    def __init__(self):
        self.locales = {}
        self.strings = {}
        self.poke = {}
        self.evolutions = {}

        self.loadStrings()
        self.loadPoke()
        self.loadPokeEvos()


    def loadStrings(self):
        subfolders = [ f.name for f in os.scandir("./files/resources/locales") if f.is_dir() ]
        for folder in subfolders:
            file = './files/resources/locales/{}/strings.csv'.format(folder)
            with open(file) as f:
                reader = csv.reader(f, delimiter ="%")
                self.strings[folder] = list(reader)

    def loadPoke(self):
        subfolders = [ f.name for f in os.scandir("./files/resources/locales") if f.is_dir() ]
        for folder in subfolders:
            file = './files/resources/locales/{}/poke.csv'.format(folder)
            with open(file) as f:
                reader = csv.reader(f, delimiter ="%")
                self.poke[folder] = list(reader)

    def loadPokeEvos(self):
        subfolders = [ f.name for f in os.scandir("./files/resources/locales") if f.is_dir() ]
        for folder in subfolders:
            file = './files/resources/locales/{}/evolutions.csv'.format(folder)
            with open(file) as f:
                reader = csv.reader(f, delimiter ="%")
                self.evolutions[folder] = list(reader)


    def getLocaleFromInteraction(self, interaction):
        id = None
        if(isinstance(interaction, ContextAdapter)):
            if(interaction.getGuild() is not None):
                id = str(interaction.getGuild().id)

        elif(interaction.guild is not None):
            id = str(interaction.guild.id)


        if(id is not None):
            if(id not in self.locales.keys()):

                #Database query
                connection, cursor = getStaticReadingConn("./files/resources/bot.db")
                cursor.execute("SELECT guild_locale FROM dis_guild WHERE guild_id = ?", (id,))
                locale = cursor.fetchone()
                closeStaticConn(connection, cursor)
                self.locales[id] = locale[0]
                return locale[0]
            else:
                return self.locales[id]
        else:
            return 'en'



    def getLocalString(self, interaction, key:str, values:list):
        locale = self.getLocaleFromInteraction(interaction)
        string = None
        for row in self.strings[locale]:
            if(row[0] == key):
                string = row[1]
                break

        if string is None:
            raise KeyError("String {} has not been found".format(key))

        for tuple in values:
            string = string.replace('{'+tuple[0]+'}', str(tuple[1]))
        string = string.replace('\\n', '\n')
        return string


    def getLocalPokeString(self, interaction, key:str):
        locale = self.getLocaleFromInteraction(interaction)
        string = None
        for row in self.poke[locale]:
            if(row[0] == key):
                string = row[1]
                return string

        raise KeyError("String {} has not been found".format(key))


    def getLocalPokeEvo(self, interaction, key:str, values:list):
        locale = self.getLocaleFromInteraction(interaction)
        string = None
        for row in self.evolutions[locale]:
            if(row[0] == key):
                string = row[1]
                break

        if string is None:
            raise KeyError("String {} has not been found".format(key))

        for tuple in values:
            string = string.replace('{'+tuple[0]+'}', str(tuple[1]))
        return string


    def getPokeIdByName(self, interaction, name:str):
        locale = self.getLocaleFromInteraction(interaction)

        for row in self.poke[locale]:
            if(row[1].lower() == name.lower()):
                return int(row[0][4:])

        if(locale != "en"):
            file = './files/resources/locales/en/poke.csv'
            with open(file) as f:
                reader = csv.reader(f, delimiter ="%")

                for row in reader:
                    if(row[1].lower() == name):
                        return int(row[0][4:])
        return 0


    def updateCache(self, guildID, locale):
        self.locales[str(guildID)] = locale
