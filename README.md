# Agrarserver

### 💾 Prepare
Clone Repository and insert sample geometry shapefiles into `postgis-seed/postgis_data/antragsdaten/`

### 🏃‍Run
```sh
# create network
docker network create agrarserver-main

# start traefik
docker-compose -f traefik.yml up -d

# start container and specify your state. Please name it correct (e.g. Nordrhein-Westfalen and NOT nrw, NRW or nordrhein westfalen)!
COMPOSE_PROJECT_NAME=<state_name> docker-compose up
```
It will take some minutes until all sample data is parsed into the PostGIS DB and GeoServer started. Be patient.

PostGIS seed will print something like `postgis-seed_1  | Postgres seed is done. Bye 👋` and GeoServer will print something like `geoserver_1     | 15-Apr-2019 07:54:13.374 INFO [main] org.apache.catalina.startup.Catalina.start Server startup in 41872 ms` after startup.

##### 👯‍♀️Starting Additional Instances
If you want to start an additional instance (e.g. simulating different states) you need to clone the repository a second time, copy the data and just run. You do not need to create the network or start traefik again. The new instance will automatically connect to the `agrarserver-main` network.
```sh
COMPOSE_PROJECT_NAME=<state_name> docker-compose up
```

### 💻 Use
You can now visit e.g. http://web.Nordrhein-Westfalen.localhost and see all parcels. You can insert polygons or rectangles. Additionally, you can enable layers of other states and see its parcels when the according server is running. You can also insert geometries in other states.

Further endpoints:
- cAdvisor: http://cadvisor.nordrhein-westfalen.localhost/
- swagger: http://gateway.nordrhein-westfalen.localhost/api/ui/
- traefik: http://localhost:8000/dashboard/

### ⏫ Scale
In order to scale your services you can run `COMPOSE_PROJECT_NAME=Nordrhein-Westfalen docker-compose scale gateway=5` to have 5 running instances of the gateway service.
