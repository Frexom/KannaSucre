import csv
from connection import *

async def getLocalString(guildID:int, filename:str, key:str, values:list):

    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT guild_locale FROM guilds WHERE guild_id = ?", (guildID,))
    locale = await cursor.fetchone()
    locale = locale[0]
    await close_conn(connection, cursor)

    file = './files/ressources/locales/{}/{}.csv'.format(locale, filename)
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='&', quotechar='|')
        string = None
        for row in spamreader:
            if(row[0] == key):
                string = row[1]
                break

        if string is None:
            raise ValueError("String has not been found")

        for tuple in values:
            string = string.replace('{'+tuple[0]+'}', tuple[1])
        string = string.replace('\\n', '\n')
        return string
