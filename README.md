#  RoboShpee

## Features

  - Allows members to add themselves to certain roles,
        as well as remove and view what roles they are in.
        See `help role` for more info.
        Discord will then give a notification when a role they have is pinged.

## Run Locally

To start, create an account for your
bot; Discord.py has a great tutorial
[here](https://discordpy.readthedocs.io/en/stable/discord.html).

Then, clone the project:

```bash
  git clone git@github.com:KGB33/RoboShpee.git
  cd RoboShpee
```

```bash
cargo run
```

### Jaeger setup

To collect traces locally, run Jaeger: 

```bash
docker run -it \
    -e COLLECTOR_OTLP_ENABLED=true \
    -p 16686:16686 \
    -p 4317:4317 \
    -p 4318:4318 \
    jaegertracing/jaeger
```

Access traces at [http://localhost:16686](http://localhost:16686)

Then, run RoboShpee with `OTEL_SERVICE_NAME=roboshpee RUST_LOG="debug,h2=warn" cargo run`
