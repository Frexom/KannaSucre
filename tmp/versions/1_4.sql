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

INSERT INTO com_command(com_name, com_short, com_desc, com_use_example, com_user_perms, com_bot_perms, cat_category) VALUES ("addlevel", "Adds a level reward", "Set up and automations to give roles to your members when they reach a certain KannaSucre level!", "addlevel 5 @Role", "manage_guild", "manage_roles", 1);
INSERT INTO com_command(com_name, com_short, com_desc, com_use_example, com_user_perms, com_bot_perms, cat_category) VALUES ("editlevels", "Edits the level rewards", "View and delete the current's server level rewards!", "editlevels", "manage_guild", "manage_roles", 1);


INSERT INTO db_updates(updates) VALUES ("1.4 Done!");
