import csv
from connection import *


class Translator():
    def __init__(self, guildID:int, loadStrings:bool = False, loadPoke: bool = False):
        connection, cursor = get_static_conn("./files/ressources/bot.db")
        cursor.execute("SELECT guild_locale FROM guilds WHERE guild_id = ?", (guildID,))
        locale = cursor.fetchone()
        self.locale = locale[0]
        close_static_conn(connection, cursor)

        self.strings = None
        self.poke = None

        if(loadStrings):
            self.loadStrings()
        if(loadPoke):
            self.loadPoke()

    def loadStrings(self):
        if(self.strings is None):
            file = './files/ressources/locales/{}/strings.csv'.format(self.locale)
            with open(file) as f:
                reader = csv.reader(f, delimiter ="&")
                self.strings = list(reader)
        else:
            raise ValueError("strings.csv already loaded!")


    def loadPoke(self):
        if(self.poke is None):
            file = './files/ressources/locales/{}/poke.csv'.format(self.locale)
            with open(file) as f:
                reader = csv.reader(f, delimiter ="&")
                self.poke = list(reader)
        else:
            raise ValueError("poke.csv already loaded!")


    def getLocalString(self, key:str, values:list):
        if(self.strings is not None):
            string = None
            for row in self.strings:
                if(row[0] == key):
                    string = row[1]
                    break

            if string is None:
                raise ValueError("String has not been found")

            for tuple in values:
                string = string.replace('{'+tuple[0]+'}', str(tuple[1]))
            string = string.replace('\\n', '\n')
            return string
        else:
            raise ValueError("Must load strings.csv first")


    def getLocalPokeString(self, key:str):
        if(self.poke is not None):
            string = None
            for row in self.poke:
                if(row[0] == key):
                    string = row[1]
                    return string

            raise ValueError("String has not been found")
            
        else:
            raise ValueError("Must load poke.csv first")
