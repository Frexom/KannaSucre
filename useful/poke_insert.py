import sqlite3


def get_conn():
  conn = sqlite3.connect("database.db")
  c = conn.cursor()
  return conn, c


def close_conn(connection, cursor):
  cursor.close()
  connection.close()


def insert_pokemons():
  file1 = open('image_links', 'r')
  links = file1.readlines()
  file1.close()
  connection, cursor = get_conn()
  for link in links:
    name = link[-17:-5]
    print(name)
    number = int(name [0:4])
    alt = int(name[-7:-4])
    sex = name[-3]
    cursor.execute("SELECT * FROM table WHERE poke_id = ? and table_alt = ? and table_sex = ?", (number, alt, sex))
    query =  cursor.fetchall()
    if query == []:
      cursor.execute("INSERT INTO table (poke_id, table_alt, table_sex) VALUES(?, ?, ?)", (number, alt, sex))
    if(name[-1] == "s"):
      cursor.execute("UPDATE table SET table_shiny = ? WHERE poke_id = ? and table_alt = ? and table_sex = ?", (link, number, alt, sex))
    else:
      cursor.execute("UPDATE table SET table_normal = ? WHERE poke_id = ? and table_alt = ? and table_sex = ?", (link, number, alt, sex))
    
  connection.commit()
  cursor.close()
  close_conn(connection, cursor)



insert_pokemons()
