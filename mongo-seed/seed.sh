#!/bin/sh

mongoimport --host mongodb --db geometries --collection parcels --type json --file /parcels.json --upsert --jsonArray
mongoimport --host mongodb --db geometries --collection borders --type json --file /border.json --upsert
mongo --host mongodb /script.js
