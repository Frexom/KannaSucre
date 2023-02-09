CREATE TABLE gld_reward (
	"guild_id"	INTEGER NOT NULL,
	"rew_level"	INTEGER NOT NULL,
	"rew_role"	INTEGER,
	PRIMARY KEY("rew_level","guild_id")
);

CREATE TABLE gld_level (
    "guild_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "lev_level" INTEGER NOT NULL DEFAULT 0,
    "lev_xp" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY("guild_id", "user_id")
);

INSERT INTO com_command(com_name, com_use_example, com_user_perms, com_bot_perms, cat_category) VALUES ("addlevel", "addlevel 5 @Role", "manage_guild", "manage_roles", 1);
INSERT INTO com_command(com_name, com_use_example, com_user_perms, com_bot_perms, cat_category) VALUES ("editlevels","editlevels", "manage_guild", "manage_roles", 1);

SELECT "Please delete the column com_command.com_short and com_command.com_desc manually, as SQLite cannot do it" FROM db_updates;


INSERT INTO db_updates(updates) VALUES ("1.4 Done!");
