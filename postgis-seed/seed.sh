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
shp2pgsql -s 4326 -W "latin1" postgis_data/bundeslaender/vg2500_bld bundeslaender | psql -U $user -d $db -h $host -q
shp2pgsql -s 4326 postgis_data/antragsdaten/Antragsdaten_2017_LE_4326 landschaftselemente | psql -U $user -d $db -h $host -q
shp2pgsql -s 4326 postgis_data/antragsdaten/Antragsdaten_2017_NETTO_4326 nettoflaechen | psql -U $user -d $db -h $host -q

>&2 echo "Postgres is done"