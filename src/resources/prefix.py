from src.resources.connection import closeStaticConn, getStaticReadingConn


class Prefix:
    prefixes: dict = {}

    def __fetch_prefix(guild_id):
        connection, cursor = getStaticReadingConn()
        cursor.execute("SELECT guild_prefix FROM dis_guild WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        closeStaticConn(connection, cursor)
        return result[0]

    def get_prefix(messageOrBot, message=None):
        if isinstance(message, Prefix):
            raise ValueError("'get_prefix' is a static method.")

        if message is None:
            message = messageOrBot

        if message.guild is None:
            return "!"

        if message.guild.id in Prefix.prefixes.keys():
            return Prefix.prefixes[message.guild.id]
        else:
            Prefix.prefixes[message.guild.id] = Prefix.__fetch_prefix(message.guild.id)
            return Prefix.prefixes[message.guild.id]

    def updateCache(guild_id, prefix):
        if isinstance(guild_id, Prefix):
            raise ValueError("'update_cache' is a static method.")

        Prefix.prefixes[guild_id] = prefix
