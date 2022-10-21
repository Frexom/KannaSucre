import sqlite3

def get_conn(i):
	if(i == 1):
		connection = sqlite3.connect("new.db")
		cursor = connection.cursor()
		return connection, cursor

	connection = sqlite3.connect("bot.db")
	cursor = connection.cursor()
	return connection, cursor



def poketransfer():
	connection1 = sqlite3.connect("new.db")
	cursor1 = connection1.cursor()

	connection2 = sqlite3.connect("bot.db")
	cursor2 = connection2.cursor()
	cursor2.execute("DELETE FROM pokedex")
	connection2.commit()

	print("pokedex purge done")


	cursor1.execute("SELECT max(ROWID) FROM pokedex")
	count = cursor1.fetchone()
	count = count[0]
	print(count)

	for i in range(count):
		cursor1.execute("SELECT poke_id, poke_name, poke_desc, poke_rarity FROM pokedex WHERE ROWID = ?", (i+1, ))
		bip = cursor1.fetchone()
		if bip != None:
			cursor2.execute("INSERT INTO pokedex (poke_id, poke_name, poke_desc, poke_rarity) VALUES (?, ?, ?, ?)", (bip[0], bip[1], bip[2], bip[3]))
	connection2.commit()



	cursor2.execute("DELETE FROM evolutions")
	connection2.commit()

	print("evolutions purge done")


	cursor1.execute("SELECT max(ROWID) FROM evolutions")
	count = cursor1.fetchone()
	count = count[0]
	print(count)

	for i in range(count):
		cursor1.execute("SELECT evo_pre, evo_post, evo_pre_alt, evo_post_alt, evo_method FROM evolutions WHERE ROWID = ?", (i+1, ))
		bip = cursor1.fetchone()
		if bip != None:
			cursor2.execute("INSERT INTO evolutions (evo_pre, evo_post, evo_pre_alt, evo_post_alt, evo_method) VALUES (?, ?, ?, ?, ?)", (bip[0], bip[1], bip[2], bip[3], bip[4]))
	connection2.commit()




poketransfer()
