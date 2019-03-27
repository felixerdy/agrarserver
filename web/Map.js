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

const baseUrl = "http://localhost:8080";
const flaskURL = "http://localhost:5000";

const gatewayURL = "http://localhost:5000";

const geometryIntersectXML = parameter => `<?xml version="1.0" encoding="UTF-8"?><wps:Execute version="1.0.0" service="WPS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
<ows:Identifier>gs:IdentifyOverlaps</ows:Identifier>
<wps:DataInputs>
<wps:Input>
<ows:Identifier>polygon</ows:Identifier>
<wps:Data>
  <wps:ComplexData mimeType="application/json">
    <![CDATA[
${parameter}
]]>
  </wps:ComplexData>
</wps:Data>
</wps:Input>
</wps:DataInputs>
<wps:ResponseForm>
<wps:RawDataOutput mimeType="application/json">
<ows:Identifier>result</ows:Identifier>
</wps:RawDataOutput>
</wps:ResponseForm>
</wps:Execute>`;

const geometryInsertXML = coordinateList => `<?xml version="1.0"?>
<wfs:Transaction
   version="2.0.0"
   service="WFS"
   xmlns:fes="http://www.opengis.net/fes/2.0"
   xmlns:gml="http://www.opengis.net/gml/3.2"
   xmlns:wfs="http://www.opengis.net/wfs/2.0"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.opengis.net/wfs/2.0
                       http://schemas.opengis.net/wfs/2.0/wfs.xsd
                       http://www.opengis.net/gml/3.2
                       http://schemas.opengis.net/gml/3.2.1/gml.xsd">
   <wfs:Insert>
    <parcels>
      <geometry>
        <gml:Polygon>
         <gml:exterior>
            <gml:LinearRing>
               <gml:posList>
              ${coordinateList.flat().join(" ")}
            	</gml:posList>
            </gml:LinearRing>
         </gml:exterior>
      </gml:Polygon>
      </geometry>
    </parcels>
    <!-- you can insert multiple features if you wish-->
   </wfs:Insert>
</wfs:Transaction>`;

export default () => {
  var map = L.map("map", {
    drawControl: true
  }).setView([51.505, 9], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  fetch(
    `${flaskURL}/api/bundeslaender`
  )
    .then(res => res.json())
    .then(data => L.geoJSON(data).addTo(map));

  const nettoflaechen = L.tileLayer
    .wms(`${baseUrl}/geoserver/felix/wms?`, {
      layers: "felix:nettoflaechen",
      transparent: true,
      format: "image/png"
    })
    .addTo(map);

  L.tileLayer
    .wms(`${baseUrl}/geoserver/felix/wms?`, {
      layers: "felix:landschaftselemente",
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
    fetch(`${flaskURL}/api/wfs/overlappingPolygons`, {
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
        if (data.numberMatched > 0) {
          notPermittedLayer.addData(data)
        } else {
          fetch(`${flaskURL}/api/wfs/insertGeometry`, {
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
        }
      })
      .catch(error => {
        console.log(error);
      });
  });
};
