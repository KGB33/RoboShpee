#  RoboShpee

## Features

  - Allows members to add themselves to certain roles,
        as well as remove and view what roles they are in.
        See `help role` for more info.
        Discord will then give a notification when a role they have is pinged.
  - Can print its own source code via the `quine` command.
  - Url Shortener Integration via the `url` command.
        For more info see [here](https://github.com/KGB33/url-shortener).
  - Embedded Memes. (`cs` and `taco_time` commands)
  - Get the status of the Minecraft server.


## Run Locally

First, create an account for your bot, Discord.py has a great
tutorial [here](https://discordpy.readthedocs.io/en/stable/discord.html).

Then, clone the project:

```bash
  git clone git@github.com:KGB33/RoboShpee.git
  cd RoboShpee
```

Create and activate a new virtual environment, install the dependencies,
and start the bot.

```bash
python -m venv .venv
. .venv/bin/activate && python -m pip install --upgrade pip
pip install pyproject.toml

DISCORD_TOKEN=YOUR_TOKEN_HERE python -m roboshpee
```
