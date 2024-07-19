test:
    dagger call \
        --lockfile uv.dev.lock \
        --pyproject pyproject.toml \
        --src roboshpee \
        test \
        --tests tests

run:
    dagger call \
        --lockfile uv.dev.lock \
        --pyproject pyproject.toml \
        --src roboshpee \
        run \
        --token DISCORD_TOKEN
