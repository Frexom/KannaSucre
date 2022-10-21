from connection import *
from mentions import *
from prefix import *
from bot import *

sys.path.append("../ressources")


poke_count = 809



def get_rarity():
  rand = random.randint(1, 100)
  if rand == 100:
    return [5, "legendary"]
  elif rand >= 95 and rand <= 99:
    return [4, "Super Rare"]
  elif rand >= 80 and rand <=94:
    return [3, "Rare"]
  elif rand >= 55 and rand <=79:
    return [2, "Uncommon"]
  else:
    return [1, "Common"]



def get_shiny():
  rand = random.randint(1, 256)
  if rand == 1:
    return True
  return False




async def get_alt(poke_id):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT DISTINCT pokelink_alt FROM pokelink WHERE poke_id = ?", (poke_id, ))
  alt = await cursor.fetchall()
  await close_conn(connection, cursor)
  if len(alt) == 1:
    return alt[0][0]
  else:
    return alt[random.randint(0, len(alt)-1)][0]


async def get_pokemon_sex(poke_id, poke_alt):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT pokelink_sex FROM pokelink WHERE poke_id = ? AND pokelink_alt = ?", (poke_id, poke_alt))
  data = await cursor.fetchall()
  await close_conn(connection, cursor)
  if len(data) == 1:
    return data[0][0]
  else:
    return data[random.randint(0,len(data)-1)][0]



async def get_pokemon_id(rarity):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT poke_id, poke_name FROM pokedex WHERE poke_rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity, ))
  temp =  await cursor.fetchone()
  await close_conn(connection, cursor)
  return temp



async def get_pokemon_details(bot):
  rarity = get_rarity()
  poke_id = await get_pokemon_id(rarity[0])
  shiny = get_shiny()
  poke_alt = await get_alt(poke_id[0])
  poke_sex = await get_pokemon_sex(poke_id[0], poke_alt)
  connection, cursor = await get_conn("./files/ressources/bot.db")
  if shiny:
    await cursor.execute("SELECT pokelink_shiny FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
  else:
    await cursor.execute("SELECT pokelink_normal FROM pokelink WHERE poke_id = ? and pokelink_alt = ? and pokelink_sex = ?", (poke_id[0], poke_alt, poke_sex))
  link = await cursor.fetchone()
  await close_conn(connection, cursor)
  return [poke_id[0], poke_id[1], rarity[0], rarity[1],poke_alt, shiny, poke_sex, link[0]]




@bot.command(name="poke")
async def poke(ctx):
  if not ctx.author.bot :
    await ctx.channel.typing()
    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (ctx.author.id, ))
    data = await cursor.fetchone()
    last_roll = data[0]
    pity = data[1]
    now = time.time()
    time_since = int(now - last_roll)
    if time_since > 7200 or pity >= 1:
      if time_since < 7200:
        pity -= 1
        await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity, ctx.author.id))
      else:
        await cursor.execute("UPDATE users SET user_last_roll_datetime = ? WHERE user_id = ?", (now, ctx.author.id))
      await connection.commit()

      pokemon_details = await get_pokemon_details(bot)

      await cursor.execute("SELECT * FROM pokemon_obtained WHERE user_id = ? AND poke_id = ? AND pokelink_alt = ?", (ctx.author.id, pokemon_details[0], pokemon_details[4] ))
      is_obtained = await cursor.fetchone()
      shiny_string = ""
      is_shiny = pokemon_details[5]
      if is_shiny:
        shiny_string = "\nWait!! Is it shiny??? :sparkles:"
      if is_obtained == None:
        await cursor.execute("INSERT INTO pokemon_obtained (user_id, poke_id, pokelink_alt, is_shiny, date) VALUES (?, ?, ?, ?, ?)", (ctx.author.id, pokemon_details[0], pokemon_details[4], int(is_shiny), now))
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string
      elif (is_obtained[3] == 0 and is_shiny):
        await cursor.execute("UPDATE pokemon_obtained SET is_shiny = 1 WHERE user_id = ? and poke_id = ?", (ctx.author.id, pokemon_details[0]))
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string
      else:
        desc = "This is a **" + pokemon_details[3] + "** pokemon!" + shiny_string + "\nYou already had that pokemon.:confused:\nRolls +" + str(0.25*pokemon_details[2]) + "."
        await cursor.execute("UPDATE users SET user_pity = ? WHERE user_id = ?", (pity+0.25*pokemon_details[2], ctx.author.id))
      await connection.commit()
      e = discord.Embed(title = "Congratulation **" + str(ctx.author.display_name) + "**, you got **" + pokemon_details[1] + "**!",  description = desc)
      e.set_image(url=pokemon_details[-1])
      await ctx.send(embed = e)
    else:
      time_left = int(7200 - time_since)
      if time_left > 3600:
        time_left -= 3600
        time_left = int(time_left/60)
        await ctx.send(str(ctx.author.display_name) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
      else:
        time_left += 60
        time_left = int(time_left/60)
        await ctx.send(str(ctx.author.display_name) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
    await close_conn(connection, cursor)



async def get_pokeinfo_embed(poke_id, page, shiny):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT poke_id, poke_name, pokelink_sex, pokelink_normal, pokelink_shiny, poke_desc, pokelink_label FROM pokelink JOIN pokedex USING(poke_id) WHERE poke_id = ?;", (poke_id, ))
  pokedetails = await cursor.fetchall()

  page = page % len(pokedetails)
  poke_sex = ""
  if(pokedetails[page][2] == "f"):
    poke_sex = "\u2640"
  if(pokedetails[page][2] == "m"):
    poke_sex = "\u2642"


  if(shiny):
    e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + ":sparkles: " + poke_sex, description = pokedetails[page][6] + " form")
    e.set_image(url=pokedetails[page][4])
  else:
    e = discord.Embed(title = "N°" + str(poke_id) + " : " + pokedetails[page][1] + poke_sex, description = pokedetails[page][6] + " form")
    e.set_image(url=pokedetails[page][3])

  e.add_field(name = "Description : ", value=pokedetails[page][5])
  e.set_footer(text = "page " + str(page+1) + "/" + str(len(pokedetails)))
  return e



@bot.command(name="pokeinfo")
async def pokeinfo(ctx):
  if not ctx.author.bot:
    message = ctx.message.content.split(" ")
    if len(message) > 1:
      connection, cursor = await get_conn("./files/ressources/bot.db")
      pokemon = message[1]
      try:
        if not pokemon.isdecimal():
          await cursor.execute("SELECT poke_id FROM pokedex WHERE lower(poke_name) = lower(?)", (pokemon, ))
          poke_id = await cursor.fetchone()
          poke_id = poke_id[0]
        else:
          poke_id = int(message[1])
        if poke_id > poke_count or poke_id <= 0 :
          raise TypeError
        print('AAA')
        msg = await ctx.send(embed=await get_pokeinfo_embed(poke_id, 0, False))
        await msg.add_reaction('◀')
        await msg.add_reaction('✨')
        await msg.add_reaction('▶')
        await asyncio.sleep(1)

        def check(r, a):
          return r.message == msg


        page = 0
        shiny = False
        active = True
        while(active):
          try:
            a = await bot.wait_for("reaction_add", check = check, timeout = 15)
            if a[0].emoji == '▶':
              page = (page + 1)
            elif a[0].emoji == '◀':
              page = (page - 1)
            elif a[0].emoji == '✨':
              shiny = not shiny

            await msg.edit(embed=await get_pokeinfo_embed(poke_id, page, shiny))
          except asyncio.TimeoutError:
            active = False
      except TypeError:
        e = discord.Embed(title = "Not found :(", description = "No such pokemon")
        await ctx.send(embed = e)

    else:
      await ctx.channel.send("```" + await get_pre(ctx.message) + "pokeinfo *number/name of pokemon*```")

  else:
    await ctx.send("This command isn't supported for bots.")


@bot.command(name="rolls")
async def rolls(ctx):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT user_last_roll_datetime, user_pity FROM users WHERE user_id =?", (ctx.author.id, ))
  data = await cursor.fetchone()
  last_roll = data[0]
  pity = data[1]
  now = time.time()
  time_since = int(now - last_roll)
  time_left = int(7200 - time_since)
  if time_left <= 0:
    await ctx.send(str(ctx.author.display_name) + ", your poke roll is available.\nRolls : `" + str(pity)+ "`.")
  elif time_left > 3600:
    time_left -= 3600
    time_left = int(time_left/60)
    await ctx.send(str(ctx.author.display_name) + ", your next roll will be available in 1 hour " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
  else:
    time_left += 60
    time_left = int(time_left/60)
    await ctx.send(str(ctx.author.display_name) + ", your next roll will be available in " + str(time_left) + " minutes.\nRolls : `" + str(pity)+ "`.")
  await close_conn(connection, cursor)






async def get_pokedex_embed(user, page):
  connection, cursor = await get_conn("./files/ressources/bot.db")
  await cursor.execute("SELECT DISTINCT poke_id, poke_name, is_shiny FROM pokedex JOIN pokemon_obtained USING(poke_id) WHERE user_id = ? ORDER BY poke_id;", (user.id, ))
  Pokemons = await cursor.fetchall()
  await cursor.execute("SELECT COUNT(DISTINCT poke_id) FROM pokemon_obtained WHERE user_id = ?;", (user.id, ))
  number_of_pokemons = await cursor.fetchone()
  number_of_pokemons = number_of_pokemons[0]
  if Pokemons == [] :
    list_pokemons = "No pokemons."
  else:
    list_pokemons = ""
    list_index = 0
    while(Pokemons[list_index][0] <= page*20 and list_index != len(Pokemons)-1) :
      list_index += 1
    for i in range(page*20, page*20+20):
      if i < poke_count:
        if Pokemons[list_index][0] == i+1:
          if Pokemons[list_index][2]:
            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + ":sparkles:\n"
          else:
            list_pokemons += str(i+1) + " - " + Pokemons[list_index][1] + "\n"
          if list_index < len(Pokemons)-1:
            list_index += 1
        else:
          list_pokemons += str(i+1) + " - --------\n"
  embed=discord.Embed(title = str(user.display_name) + "'s Pokedex", description = str(number_of_pokemons) + "/" + str(poke_count) + " pokemons")
  embed.set_thumbnail(url="https://www.g33kmania.com/wp-content/uploads/Pokemon-Pokedex.png")
  embed.add_field(name="Pokemons :", value=list_pokemons, inline=True)
  embed.set_footer(text = "page " + str(page+1) + "/" + str(int(poke_count/20)+1))
  await close_conn(connection, cursor)
  return embed


@bot.command(name="pokedex")
async def pokedex(ctx):
  if not ctx.author.bot :
    user = get_target(ctx)
    if not user.bot:
      message = ctx.message.content.split(" ")
      page = 0
      if len(message) > 1 and message[1].isdecimal() :
        page = int(message[1])
        page -= 1
        if page < 1 or page > int(poke_count/20)+1:
          page = 0

      msg = await ctx.send(embed=await get_pokedex_embed(user, page))
      await msg.add_reaction('◀️')
      await msg.add_reaction('▶️')
      await asyncio.sleep(1)

      def check(r, a):
        return r.message == msg


      active = 1
      while(active == 1):
        try:
          a = await bot.wait_for("reaction_add", check = check, timeout = 15)
          if a[0].emoji == '▶️':
            page = (page + 1) % (int(poke_count/20)+1)
          elif a[0].emoji == '◀️':
            page = (page - 1) % (int(poke_count/20)+1)
          await msg.edit(embed=await get_pokedex_embed(user, page))
        except asyncio.TimeoutError:
          active = 0


    else:
      await ctx.send("This command isn't supported for bots.")


@bot.command(name="pokerank")
async def pokerank(ctx):
  if not ctx.author.bot :
    await ctx.channel.typing()

    def sort_on_pokemon(e):
      return e[0]


    connection, cursor = await get_conn("./files/ressources/bot.db")
    await cursor.execute("SELECT COUNT(DISTINCT poke_id), user_id FROM pokemon_obtained GROUP BY user_id LIMIT 10")
    result = await cursor.fetchall()
    await close_conn(connection, cursor)
    result_list = []
    for i in range(len(result)):
      result_list.append([result[i][0], result[i][1]])
    result_list.sort(reverse=True, key=sort_on_pokemon)
    description = ""
    limit = 10
    i = 0
    ranking = 0
    while i != len(result_list) and ranking < 10:
      user = await bot.fetch_user(result_list[i][1])
      if user != None:
        ranking += 1;
        description += str(ranking) + "-" + displayuser.display_name + " - " + str(result_list[i][0]) + "/" + str(poke_count) + "\n"
      i += 1
    embed=discord.Embed(title= "KannaSucre's Pokerank", colour=discord.Colour(0x635f))
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Ranking :", value=description)
    await ctx.send(embed=embed)
