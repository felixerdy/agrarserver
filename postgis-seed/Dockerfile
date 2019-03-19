FROM mdillon/postgis:11-alpine

COPY postgis_data /postgis_data
COPY seed.sh /seed.sh

ENTRYPOINT ./seed.sh