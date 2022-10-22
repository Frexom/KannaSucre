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
        if link != '':
            name = link[-16:-5]
            print(name)
            number = int(name [0:3])
            alt = int(name[-7:-4])
            sex = name[-3]
            cursor.execute("SELECT * FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (number, alt, sex))
            query =  cursor.fetchall()
            if query == []:
                cursor.execute("INSERT INTO pokelink (poke_id, pokelink_alt, pokelink_sex) VALUES(?, ?, ?)", (number, alt, sex))
            if(name[-1] == "s"):
                cursor.execute("UPDATE pokelink SET pokelink_shiny = ? WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (link, number, alt, sex))
            else:
                cursor.execute("UPDATE pokelink SET pokelink_normal = ? WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (link, number, alt, sex))

    connection.commit()
    cursor.close()
    close_conn(connection, cursor)



insert_pokemons()
