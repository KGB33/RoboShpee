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

There are two ways to run locally, both start with creating an account for your
bot; Discord.py has a great tutorial
[here](https://discordpy.readthedocs.io/en/stable/discord.html).

Then, clone the project:

```bash
  git clone git@github.com:KGB33/RoboShpee.git
  cd RoboShpee
```

### The Normal Way

Install Python ^3.11 and UV.

Then create and activate a new virtual environment, install the dependencies,
and start the bot.

```bash
uv venv
. .venv/bin/activate
uv pip install pyproject.toml

DISCORD_TOKEN=YOUR_TOKEN_HERE python -m roboshpee
```

### The "Simple Way"

Install Dagger, then just `dagger call run --token env:DISCORD_TOKEN`.

# Rust rewrite

Oftentimes, slash commands would fail to respond in time and would thus be killed by Discord.
I'm not rewriting it in rust just for speed, but because:
  - I don't want to manage/deploy heavy Docker containers
  - I (now) prefer strongly typed languages.
  - Adding telemetry seems like fun, and could be a good rust meetup topic.


## Jaeger setup

Run Jaeger: 

```bash
 podman run --replace --name jaeger \
    -e COLLECTOR_OTLP_ENABLED=true \
    -p 16686:16686 \
    -p 4317:4317 \
    -p 4318:4318 \
    jaegertracing/jaeger
```

Access traces at [http://localhost:16686](http://localhost:16686)

Then, run RoboShpee with `OTEL_SERVICE_NAME=roboshpee RUST_LOG="debug,h2=warn" cargo run`
