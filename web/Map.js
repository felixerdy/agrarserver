import L from "leaflet";
import "leaflet/dist/leaflet.css";

import * as Draw from "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

/* This code is needed to properly load the images in the Leaflet CSS */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

const GATEWAY_HOST = `http://${process.env.GATEWAY_HOST}`

const initMap = () => {
  var map = L.map("map").setView([51.505, 9], 6);

  var drawControl = new L.Control.Draw({
    draw: {
      rectangle: true,
      polygon: true,
      marker: false,
      polyline: false,
      circle: false,
      circlemarker: false
    }
  });
  map.addControl(drawControl);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  fetch(
    `${GATEWAY_HOST}/api/bundeslaender`
  )
    .then(res => res.json())
    .then(data => L.geoJSON(data).addTo(map));

  const nettoflaechen = L.tileLayer
    .wms(`${GATEWAY_HOST}/api/wms/nettoflaechen?`, {
      layers: "felix:nettoflaechen",
      transparent: true,
      format: "image/png"
    })
    .addTo(map);

  var notPermittedStyle = {
    color: "red",
    weight: 5,
    opacity: 0.65
  };
  var notPermittedLayer = L.geoJSON(null, {
    style: notPermittedStyle
  }).addTo(map);

  map.on(L.Draw.Event.CREATED, e => {
    var geometry = e.layer.toGeoJSON();
    console.log(geometry)
    fetch(`${GATEWAY_HOST}/api/wfs/insertGeometry`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        typeName: "nettoflaechen",
        polygon: geometry
      })
    })
      .then(res => res.json())
      .then(data => {
        console.log(data)
        nettoflaechen.setParams({ fake: Date.now() }, false)
      })
  });
}

export default () => {
  initMap()
};
