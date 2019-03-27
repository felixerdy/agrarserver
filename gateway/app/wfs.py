from flask import request
import requests
import base64
import urllib.parse
import json
import os
import xmltodict


GEOSERVER_HOST = os.getenv('GEOSERVER_HOST', "localhost")
GEOSERVER_PORT = os.getenv('GEOSERVER_PORT', "8080")

BASE_URL = f'http://{GEOSERVER_HOST}:{GEOSERVER_PORT}/geoserver/wfs'

# BASE_URL = 'http://localhost:8080/geoserver/wfs'
data_string = 'admin:geoserver'
data_bytes = data_string.encode("utf-8")
AUTH = base64.b64encode(data_bytes).decode("utf-8")

SAMPLE_TYPE_NAME = 'nettoflaechen'
SAMPLE_POS_LIST = '5.527008 51.679171 5.527008 52.17188 8.549622 52.17188 8.549622 52.679171 5.527008 51.679171'


def getXMLBody(typeName, posList):
    return f"""<?xml version="1.0"?>
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
            <{typeName}>
                <geom>
                    <gml:MultiSurface>
                        <gml:surfaceMembers>
                            <gml:Polygon>
                                    <gml:exterior>
                                        <gml:LinearRing>
                                            <gml:posList>
                                                {posList}
                                            </gml:posList>
                                        </gml:LinearRing>
                                    </gml:exterior>
                                </gml:Polygon>
                        </gml:surfaceMembers>
                    </gml:MultiSurface>
                </geom>
            </{typeName}>
            <!-- you can insert multiple features if you wish-->
        </wfs:Insert>
        </wfs:Transaction>"""


def getBundeslandContainsXMLQuery(typeName, valueReference, posList):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <wfs:GetFeature service="WFS" version="2.0.0" outputFormat="application/json"
            xmlns:fes="http://www.opengis.net/fes/2.0"
            xmlns:gml="http://www.opengis.net/gml/3.2"
            xmlns:wfs='http://www.opengis.net/wfs/2.0'
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/wfs/2.0
                                http://schemas.opengis.net/wfs/2.0/wfs.xsd
                                http://www.opengis.net/gml/3.2
                                http://schemas.opengis.net/gml/3.2.1/gml.xsd">
            <wfs:Query typeNames="{typeName}">
                <fes:Filter>
                <fes:Contains>
                    <fes:ValueReference>{valueReference}</fes:ValueReference>
                    <gml:Polygon srsName="urn:ogc:def:crs:EPSG::4326">
                                    <gml:exterior>
                                        <gml:LinearRing>
                                            <gml:posList>{posList}</gml:posList>
                                        </gml:LinearRing>
                                    </gml:exterior>
                            </gml:Polygon>
                </fes:Contains>
                </fes:Filter>
            </wfs:Query>
        </wfs:GetFeature>"""


def getOverlapXMLQuery(typeName, valueReference, posList):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <wfs:GetFeature service="WFS" version="2.0.0" outputFormat="application/json"
            xmlns:wfs="http://www.opengis.net/wfs/2.0"
            xmlns:fes="http://www.opengis.net/fes/2.0"
            xmlns:gml="http://www.opengis.net/gml/3.2"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/wfs/2.0
                                http://schemas.opengis.net/wfs/2.0/wfs.xsd
                                http://www.opengis.net/gml/3.2
                                http://schemas.opengis.net/gml/3.2.1/gml.xsd">
            <wfs:Query typeNames="{typeName}">
                <fes:Filter>
                    <fes:Intersects>
                        <fes:ValueReference>{valueReference}</fes:ValueReference>
                        <gml:Polygon>
                            <gml:exterior>
                                <gml:LinearRing>
                                    <gml:posList>{posList}</gml:posList>
                                </gml:LinearRing>
                            </gml:exterior>
                        </gml:Polygon>
                    </fes:Intersects>
                </fes:Filter>
            </wfs:Query>
        </wfs:GetFeature>"""


def insertGeometry():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """
    # get request body data
    TYPE_NAME = request.get_json().get('typeName', 'nettoflaechen')
    VALUE_REFERENCE = request.get_json().get('valueReference', 'geom')
    POLYGON = request.get_json().get('polygon')

    print(POLYGON)

    # reverse polygon coordinates and make a flat list
    REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                               for y in x]

    # stringify flattened list
    REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in REVERSED_POLYGON_COORDS])

    data = getXMLBody(TYPE_NAME, REVERSED_POLYGON_COORDS_JOINED)
    # set what your server accepts
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)

    dictResponse = xmltodict.parse(r.text)

    return json.loads(json.dumps(dictResponse, ensure_ascii=False))


def bundeslandContains():
    SAMPLE_NRW = "51.778564453125 7.415771484375 51.35009765625 7.415771484375  51.35009765625 7.767333984375 51.646728515625 7.767333984375 51.778564453125 7.415771484375"

    data = getBundeslandContainsXMLQuery("bundeslaender", "geom", SAMPLE_NRW)
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)
    return json.loads(r.text)


def overlappingPolygons():
    # get request body data
    TYPE_NAME = request.get_json().get('typeName', 'nettoflaechen')
    VALUE_REFERENCE = request.get_json().get('valueReference', 'geom')
    POLYGON = request.get_json().get('polygon')

    print(POLYGON)

    # reverse polygon coordinates and make a flat list
    REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                               for y in list(reversed(x))]

    # stringify flattened list
    REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in REVERSED_POLYGON_COORDS])

    # create GeoServer post body
    data = getOverlapXMLQuery(TYPE_NAME, VALUE_REFERENCE,
                              REVERSED_POLYGON_COORDS_JOINED)
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}

    # send request to GeoServer and pipe results as response
    r = requests.post(BASE_URL, data=data, headers=headers)

    return json.loads(r.text)
