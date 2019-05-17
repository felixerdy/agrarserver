import L from "leaflet";
import "leaflet/dist/leaflet.css";

import * as Draw from "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

import 'babel-polyfill';

/* This code is needed to properly load the images in the Leaflet CSS */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

const GATEWAY_HOST = `http://${process.env.GATEWAY_HOST}`

const addPolygonWMS = async () => {
  let statePolygons = {}
  const response = await fetch(
    `${GATEWAY_HOST}/api/bundeslaender`
  )
  const data = await response.json()

  // sort states alphabetically and 
  const states = data.features.map(e => e.properties.gen).sort().filter(e => e.toLowerCase() != GATEWAY_HOST.split('.')[1].toLowerCase())
  states.forEach(state => {
    const temp = L.tileLayer
      .wms(`http://gateway.${state.toLowerCase()}.localhost/api/wms/nettoflaechen?`, {
        layers: "felix:nettoflaechen",
        transparent: true,
        format: "image/png"
      })

    statePolygons[state] = temp
  })

  return {
    "states": data,
    "statePolygons": statePolygons
  }
}

const initMap = async () => {
  const light = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  });

  const myState = L.tileLayer
    .wms(`http://gateway.${GATEWAY_HOST.split('.')[1].toLowerCase()}.localhost/api/wms/nettoflaechen?`, {
      layers: "felix:nettoflaechen",
      transparent: true,
      format: "image/png"
    })

  var map = L.map("map", {
    center: [51.505, 9],
    zoom: 6,
    layers: [light, myState]
  });

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

  const basemaps = {
    "Light": light
  }

  addPolygonWMS().then(data => {
    L.geoJSON(data.states, {
      style: {
        color: 'grey',
        weight: 3,
        opacity: 0.5
      }
    }).addTo(map)
    L.control.layers(basemaps, data.statePolygons).addTo(map);
  })

  var notPermittedLayer = L.geoJSON(null, {
    style: {
      color: "red",
      weight: 5,
      opacity: 0.65
    }
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
        notPermittedLayer.clearLayers()
        if (data.error == "overlaps") {
          notPermittedLayer.addData(data.data)
        }
        else if (data.error == 'outsideOfState') {
          if (data.postResponse.error == 'overlaps') {
            notPermittedLayer.addData(data.postResponse.data)
          } else {
            const stateName = data.data.features[0].properties.gen.toLowerCase()
            map.eachLayer(layer => {
              if (layer instanceof L.TileLayer && layer._url.includes(stateName))
                layer.setParams({ fake: Date.now() }, false)
            });
          }
        }
        else if (data['wfs:TransactionResponse']['wfs:TransactionSummary']['wfs:totalInserted'] == 1) {
          myState.setParams({ fake: Date.now() }, false)
        }

      })
  });
}

export default () => {
  initMap()
};
