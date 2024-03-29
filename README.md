
# KannaScure
<div align ="right" style="float:right">
<p align ="right">Profile picture by <a href = "https://www.instagram.com/evantilateur/">@evantilateur</a></p>
<a href="https://www.instagram.com/evantilateur/">
<img width="200" height="183" align ="right" src="https://images-ext-1.discordapp.net/external/dmI01a7agg5IkxCw99zIx6pGzxLpjV-DhXw5c19_eqk/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/765255086581612575/7c22fc11719a33900655d6bf457417c7.png?width=660&height=660">
</a>
</div>


This repository is the source code of a Discord bot created from scratch by myself. It can do a variety of things, and I'm updating it regulary by adding new commands, languages, etc...
At the moment, the bot is available in English and French, but i'm looking for foreign people to help me translate the bot!

## Commands

### Admin commands :

`addlevel` : Adds a level rewards.

`announce` : Sends a custome message to a channel.

`ban` : Bans a member.

`editlevels` : View/delete the level rewards.

`giveaway` : Starts a new giveaway! (slash command only)

`language` : Changes the bot's language!

`prefix` : Changes the bot's prefix.

`togglelevels` : Toggles the level feature.

`welcome` : Defines the welcome channel/role.


### Moderation commands :

`clear` : Clears some messages.

`kick` : Kicks a member.

`prune` : Deletes an user's messages.


### Utilities commands :

`dice` : Rolls a dice

`help` : Shows the commands details

`servericon` : Posts the server's icon

`supportserver` : Sends an inite to KannaSucre's server!

`usericon` : Displays an user's icon.


### Miscellaneous/Fun commands :

`hug` : Hugs someone!

`level` : Displays your level and XP.

`poke` : Catches a Pokémon!

`pokedex` : Displays your Pokédex.

`pokeinfo` : Displays a Pokémon's infos.

`pokerank` : Shows the best pokemon trainers!

`rolls` : Show poke command personnal details.

`stand` : Displays your assigned stand.


For more infos, see the bot's /help command in discord.
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TOKEN` : Your discord bot token

`OWNER_ID` : Your personnal Discord ID (or the ID of the person who will be in charge of the bot)

`TESTGUILDID` : The Discord ID of the guild you'll use to make tests

`SUPPORTSERVERLINK` : A link to your bot's support server

## Run Locally

Clone the project

```bash
  git clone https://github.com/Frexom/KannaSucre
```

Go to the project directory

```bash
  cd KannaSucre
```

Install dependencies

```bash
  poetry install
```

Set the database

```bash
  cp tmp/bot.db files/resources/database/bot.db
```

Start the bot!

```bash
  python3 -m src.main
```

## Keeping the bot updated
To keep the bot updated, wait for a new version ot release for the bot to be in a stable state. If the database has been changed in the newer version, just update yours with the sql scripts in /tmp/versions :

```bash
  sqlite3 files/resources/database/bot.db < tmp/versions/*version*.sql
```

If you're multiple releases late, make sure to use every SQL script on your database, in chronological order.

Note: Performed database updates can be checked in the db_updates table!


## Important links


Top.gg bot page : <a href="https://top.gg/bot/765255086581612575">
  <img src="https://top.gg/api/widget/owner/765255086581612575.svg">
</a>

Support Server invite : [Click here](https://discord.gg/68UVAfGY85)

KannaSucre Crowdin project : [Click here](https://crowdin.com/project/kannasucre)

Shiny Sugimori sprites : [Click here](https://www.deviantart.com/tonofdirt726)<br>
(Thank you a lot for letting me use them!)

## Authors

- [@frexom](https://www.github.com/ferxom) (The owner of this repo)
