#!/bin/bash
tag="redis"
docker build -t ${tag} .
docker run -d -p 6379:6379 --name ${tag} --rm ${tag}
