#!/bin/bash

# variables
user=postgres
db=pgis
host=postgis

until psql -h $host -U $user -c '\q'; do
  echo >&2 "Postgres is unavailable - sleeping 😴"
  sleep 1
done

echo >&2 "Postgres is up 🤩 - executing seed..."

# Check if database exists in PostgreSQL using shell -> https://stackoverflow.com/a/16783253/5660646
if psql -h $host -U $user -lqt | cut -d \| -f 1 | grep -qw $db; then
  # database exists
  echo >&2 "Postgres DB $db already exists 😏"
else
  createdb $db -h $host -U $user
  psql -h $host -d $db -U $user -c 'create extension postgis;'
  shp2pgsql -s 4326 -W "latin1" postgis_data/bundeslaender/vg2500_bld bundeslaender | psql -U $user -d $db -h $host -q
  shp2pgsql -s 4326 postgis_data/antragsdaten/Antragsdaten_2017_LE_4326 landschaftselemente | psql -U $user -d $db -h $host -q
  shp2pgsql -s 4326 postgis_data/antragsdaten/Antragsdaten_2017_NETTO_4326 nettoflaechen | psql -U $user -d $db -h $host -q
fi

echo >&2 "Postgres seed is done. Bye 👋"
