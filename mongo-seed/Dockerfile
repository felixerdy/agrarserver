FROM mongo

COPY mongo_data/parcels.json /parcels.json
COPY mongo_data/border.json /border.json
COPY seed.sh /seed.sh
COPY script.js /script.js

ENTRYPOINT ./seed.sh