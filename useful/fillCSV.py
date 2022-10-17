import sqlite3


def get_conn():
  conn = sqlite3.connect("bot.db")
  c = conn.cursor()
  return conn, c


def close_conn(connection, cursor):
  cursor.close()
  connection.close()


def insert_pokemons():
  connection, cursor = get_conn()
  cursor.execute("SELECT poke_id, poke_name, poke_desc FROM pokedex ORDER BY poke_id")
  pokemons = cursor.fetchall()
  close_conn(connection, cursor)


  for i in range (len(pokemons)):
    f = open("poke.csv", "a")
    poke_id = str(pokemons[i][0])
    poke_name = str(pokemons[i][1])
    poke_desc = str(pokemons[i][2])
    f.write("\"name" + poke_id + "\",\"" + poke_name + "\"\n")
    f.write("\"desc" + poke_id + "\",\"" + poke_desc + "\"\n")




insert_pokemons()
