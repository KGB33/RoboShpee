#!/bin/bash
app="dis-bot"
docker build -t ${app} .
docker run -d -e DISCORD_TOKEN --rm ${app}
