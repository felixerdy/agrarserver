from flask import request
import base64
import urllib.parse
import json
import os
import xmltodict
import sys

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import urllib3

import functools
import urllib3

# Fix uppercase URL --> https://stackoverflow.com/a/55613184/5660646
def _custom_key_normalizer(key_class, request_context):
    """
    Create a pool key out of a request context dictionary.
    According to RFC 3986, both the scheme and host are case-insensitive.
    Therefore, this function normalizes both before constructing the pool
    key for an HTTPS request. If you wish to change this behaviour, provide
    alternate callables to ``key_fn_by_scheme``.
    :param key_class:
        The class to use when constructing the key. This should be a namedtuple
        with the ``scheme`` and ``host`` keys at a minimum.
    :type  key_class: namedtuple
    :param request_context:
        A dictionary-like object that contain the context for a request.
    :type  request_context: dict
    :return: A namedtuple that can be used as a connection pool key.
    :rtype:  PoolKey
    """
    # Since we mutate the dictionary, make a copy first
    context = request_context.copy()
    context['scheme'] = context['scheme'].lower()
    # context['host'] = context['host'].lower()

    # These are both dictionaries and need to be transformed into frozensets
    for key in ('headers', '_proxy_headers', '_socks_options'):
        if key in context and context[key] is not None:
            context[key] = frozenset(context[key].items())

    # The socket_options key may be a list and needs to be transformed into a
    # tuple.
    socket_opts = context.get('socket_options')
    if socket_opts is not None:
        context['socket_options'] = tuple(socket_opts)

    # Map the kwargs to the names in the namedtuple - this is necessary since
    # namedtuples can't have fields starting with '_'.
    for key in list(context.keys()):
        context['key_' + key] = context.pop(key)

    # Default to ``None`` for keys missing from the context
    for field in key_class._fields:
        if field not in context:
            context[field] = None

    return key_class(**context)

urllib3.util.url.NORMALIZABLE_SCHEMES = (None,)
urllib3.connectionpool.NORMALIZABLE_SCHEMES = (None,)
urllib3.poolmanager.key_fn_by_scheme['http'] = functools.partial(_custom_key_normalizer,
                                                                     urllib3.poolmanager.PoolKey)

import requests

GEOSERVER_HOST = os.getenv('GEOSERVER_HOST', "localhost")
GEOSERVER_PORT = os.getenv('GEOSERVER_PORT', '8080')


BASE_URL = f'http://{GEOSERVER_HOST}:{GEOSERVER_PORT}/geoserver/wfs'


data_string = 'admin:geoserver'
data_bytes = data_string.encode("utf-8")
AUTH = base64.b64encode(data_bytes).decode("utf-8")


def getXMLBody(typeName, valueReference, posList):
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
                <{valueReference}>
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
                </{valueReference}>
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


def bundeslandContains():
    # SAMPLE_NRW = "51.778564453125 7.415771484375 51.35009765625 7.415771484375  51.35009765625 7.767333984375 51.646728515625 7.767333984375 51.778564453125 7.415771484375"

    VALUE_REFERENCE = request.get_json().get('valueReference', 'geom')
    POLYGON = request.get_json().get('polygon')

    # reverse polygon coordinates and make a flat list
    REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                               for y in list(reversed(x))]

    # stringify flattened list
    REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in REVERSED_POLYGON_COORDS])

    return getState(VALUE_REFERENCE, REVERSED_POLYGON_COORDS_JOINED)


def getState(VALUE_REFERENCE, POLYGON):
    data = getBundeslandContainsXMLQuery(
        "bundeslaender", VALUE_REFERENCE, POLYGON)

    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)
    return json.loads(r.text)


def overlappingPolygons():
    # get request body data
    TYPE_NAME = request.get_json().get('typeName', 'nettoflaechen')
    VALUE_REFERENCE = request.get_json().get('valueReference', 'geom')
    POLYGON = request.get_json().get('polygon')

    # reverse polygon coordinates and make a flat list
    REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                               for y in list(reversed(x))]

    # stringify flattened list
    REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in REVERSED_POLYGON_COORDS])

    return checkOverlap(TYPE_NAME, VALUE_REFERENCE, REVERSED_POLYGON_COORDS_JOINED)


def checkOverlap(TYPE_NAME, VALUE_REFERENCE, REVERSED_POLYGON_COORDS_JOINED):
    # create GeoServer post body
    data = getOverlapXMLQuery(TYPE_NAME, VALUE_REFERENCE,
                              REVERSED_POLYGON_COORDS_JOINED)
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}

    # send request to GeoServer and pipe results as response
    r = requests.post(BASE_URL, data=data, headers=headers)

    return json.loads(r.text)


def postToState(STATE_NAME, TYPE_NAME, VALUE_REFERENCE, POLYGON):
    data = {
        "typeName": TYPE_NAME,
        "valueReference": VALUE_REFERENCE,
        "polygon": POLYGON
    }
    
    url = f'http://gateway.{STATE_NAME}:5000/api/wfs/insertGeometry'
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    return(r.text)


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

    # reverse polygon coordinates and make a flat list
    REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                               for y in reversed(x)]

    # stringify flattened list
    REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in REVERSED_POLYGON_COORDS])

    # check whether polygon is in one distinct state
    STATE = getState(VALUE_REFERENCE, REVERSED_POLYGON_COORDS_JOINED)
    NUMBER_MATCHED = STATE['numberMatched']

    if NUMBER_MATCHED == 0:
        return "Polygon is either not in Germany or is located in two states"

    STATE_NAME = next(iter(STATE['features']))['properties']['gen']
    # check whether polygon is in state of this gateway
    if STATE_NAME.lower() != os.getenv('STATE_NAME').lower():
        postResponse = postToState(
            STATE_NAME, TYPE_NAME, VALUE_REFERENCE, POLYGON)
        return {
            "error": "outsideOfState",
            "data": STATE,
            "postResponse": json.loads(postResponse)
        }

    # polygon is in this state, now check for overlaps
    OVERLAPS = checkOverlap(TYPE_NAME, VALUE_REFERENCE,
                            REVERSED_POLYGON_COORDS_JOINED)

    NUMBER_OF_OVERLAPS = int(OVERLAPS['numberMatched'])
    if NUMBER_OF_OVERLAPS > 0:
        return {
            "error": "overlaps",
            "data": OVERLAPS
        }

    # reverse polygon coordinates and make a flat list
    NON_REVERSED_POLYGON_COORDS = [y for x in POLYGON.get('geometry').get('coordinates')[0]
                                   for y in x]

    # stringify flattened list
    NON_REVERSED_POLYGON_COORDS_JOINED = ' '.join(
        [str(x) for x in NON_REVERSED_POLYGON_COORDS])

    # no overlaps --> insert to geoserver
    data = getXMLBody(TYPE_NAME, VALUE_REFERENCE,
                      NON_REVERSED_POLYGON_COORDS_JOINED)
    # set what your server accepts
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)

    dictResponse = xmltodict.parse(r.text)

    return json.loads(json.dumps(dictResponse, ensure_ascii=False))
