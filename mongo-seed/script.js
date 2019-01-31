conn = new Mongo("mongodb");
db = conn.getDB("geometries");
db.parcels.createIndex({ geometry: "2dsphere" });
db.borders.createIndex({ geometry: "2dsphere" });
