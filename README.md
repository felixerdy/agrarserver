# Agrarserver

# Run
```sh
# create network
docker network create agrarserver-main

# start traefik
docker-compose -f traefik.yml up -d

# start container and specify your state (e.g. Brandenburg)
COMPOSE_PROJECT_NAME=Brandenburg docker-compose up
```