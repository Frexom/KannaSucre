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
  cursor.execute("SELECT COUNT(*) FROM pokedex")
  max = cursor.fetchone()
  for i in range(max[0]):
     cursor.execute("SELECT trim(poke_desc) FROM pokedex WHERE poke_id = ?", (i+1, ))
     desc = cursor.fetchone()
     cursor.execute("UPDATE pokedex SET poke_desc = ? WHERE poke_id = ?", (desc[0], i+1))
  connection.commit()
  cursor.close()
  close_conn(connection, cursor)



insert_pokemons()
