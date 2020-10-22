# VoxelBotUtils

VoxelBotUtils is a package for extending the Discord.py library, intending to make creating bots just a lil bit faster by dealing with the overhead, like config files, help commands, and a bunch of more common utils like `TimeValue`. 

# Usage

This package is intended to be used via the commandline as a module. Running `py -m voxelbotutils --create-config-file` will create a default config file for you, and running `py -m voxelbotutils .` will run the current folder as a bot, using data in `config/config.toml` and loading the cogs from `cogs/*`.

## What's in it

You may be thinking "why the heck would I use this?"

### Database

I've included a database util! It's great! I like it! It uses PostgreSQL, using the data supplied in your [config file](voxelbotutils/config/config.example.toml). Used like so:

```py
async with self.bot.database() as db:
    await db("INSERT INTO table_name (a, b, c) VALUES ($1, $2, $3)", 1, 2, 3)
    data = await db("SELECT * FROM table_name")
for row in data:  # data is used the same as a dictionary
    print(row['a'])
```

### Redis

Redis; what a gem. I've only used it a couple of times so I'm not a big expert and I've not added a whole bunch to the util for it, but it's used in much the same way as the database in terms of SET/GET at least.

```py
async with self.bot.redis() as re:
    await re.set("KEY", "Value")
    data = await re.get("KEY")
if data is not None:
    print(data)
```

### Cooldowns

Rapptz's cooldown handling is not great if you want to do anything more complicated than "you all get cooldowns for X time". You want cooldowns in some channels and not others? You want cooldowns based on roles? That's possible with this.

```py
@voxelbotutils.command()
@utils.cooldown.cooldown(1, 60, commands.BucketType.user, cls=utils.cooldown.RoleBasedCooldown())
async def commandname(self, ctx):
    ...

@voxelbotutils.command()
@utils.cooldown.cooldown(1, 60, commands.BucketType.user, cls=utils.cooldown.CooldownWithChannelExemptions(cooldown_in=["general"]))
async def commandname(self, ctx):
    ...
```

The current cooldowns I've got built into this right now aren't really wonderful but all of the systems are there for if you want to expand it.

### Context Embeds

Setting up embeds always looked a bit messy to me, so I just added support for the `with` syntax so I could clean it up a lil. Apart from that they work pretty much identically to normal embeds.

```py
with utils.Embed() as embed:
    embed.set_author_to_user(user=self.bot.get_user(user_id))
    embed.description = "Lorem ipsum"
    embed.use_random_colour()
```


# Docs

TBA.

# Installing

The package is available via pypi - `pip install voxelbotutils` - but this package will always be further up-to-date with experimental or incomplete features should you wish to use that.
