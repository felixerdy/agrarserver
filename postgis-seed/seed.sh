#!/bin/bash

# variables
user=postgres
db=pgis
host=postgis

until psql -h $host -U $user -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing seed..."

createdb $db -h $host -U $user
psql -h $host -d $db -U $user -c 'create extension postgis;'
shp2pgsql -s 4326 -W "latin1" postgis_data/vg2500_bld bundeslaender | psql -U $user -d $db -h $host

>&2 echo "Postgres is done"