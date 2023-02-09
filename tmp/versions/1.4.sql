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

INSERT INTO db_updates(updates) VALUES ("1.4 Done!");
