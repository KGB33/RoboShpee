# Redis

Start the docker container using `./redis/start.sh`

To connect use

```Shell
username@HostMachine# docker exec -it redis bash

root@InDockerContainer:/data# redis-cli
```

From [this](https://stackoverflow.com/a/62544583/10587086) answer on StackOverflow.


The redis server is bound to `0.0.0.0` in the docker container.
