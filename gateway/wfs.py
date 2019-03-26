from flask import request
import requests
import base64
import urllib.parse
import json


BASE_URL = 'http://localhost:8080/geoserver/wfs'
data_string = 'admin:geoserver'
data_bytes = data_string.encode("utf-8")
AUTH = base64.b64encode(data_bytes).decode("utf-8")

SAMPLE_TYPE_NAME = 'nettoflaechen'
SAMPLE_POS_LIST = '5.527008 51.679171 5.527008 52.17188 8.549622 52.17188 8.549622 52.679171 5.527008 51.679171'


def getXMLBody(typeName, posList, antragsjah):
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
                <antragsjah>{antragsjah}</antragsjah>
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
                            <fes:Overlaps>
                                    <fes:ValueReference>{valueReference}</fes:ValueReference>
                                    <gml:Polygon>
                                        <gml:exterior>
                                            <gml:LinearRing>
                                                <gml:posList>{posList}</gml:posList>
                                            </gml:LinearRing>
                                        </gml:exterior>
                                    </gml:Polygon>
                    </fes:Overlaps>
                </fes:Filter>
            </wfs:Query>
        </wfs:GetFeature>"""


def insertGeometry():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """
    data = getXMLBody(SAMPLE_TYPE_NAME, SAMPLE_POS_LIST, 2019)
    # set what your server accepts
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)
    return json.loads(r.text)


def checkOverlap():

    TRIANGLE = '8.020019531249998 52.20760667286523 10.447998046875 52.234528294213646 9.426269531249998 54.03358633521085 8.020019531249998 52.20760667286523'

    # URL = f"""{BASE_URL}?
    #     &VERSION=1.0.0
    #     &SERVICE=WFS
    #     &REQUEST=GetFeature
    #     &TYPENAME={SAMPLE_TYPE_NAME}
    #     &Filter=<Filter>
    #         <Overlaps>
    #             <PropertyName>geom</PropertyName>
    #             <gml:Polygon>
    #                 <gml:outerBoundaryIs>
    #                     <gml:LinearRing>
    #                         <gml:posList>{TRIANGLE}</gml:posList>
    #                     </gml:LinearRing>
    #                 </gml:outerBoundaryIs>
    #             </gml:Polygon>
    #         </Overlaps>
    #     </Filter>"""

    URL = f'{BASE_URL}?&VERSION=1.0.0&SERVICE=WFS&REQUEST=GetFeature&TYPENAME={SAMPLE_TYPE_NAME}&Filter=<Filter><Overlaps><PropertyName>geom</PropertyName><gml:Polygon><gml:outerBoundaryIs><gml:LinearRing><gml:posList>{TRIANGLE}</gml:posList></gml:LinearRing></gml:outerBoundaryIs></gml:Polygon></Overlaps></Filter>'
    PARSED_URL = urllib.parse.quote(URL)

    return requests.get(URL).text


def bundeslandContains():
    SAMPLE_NRW = "51.778564453125 7.415771484375 51.35009765625 7.415771484375  51.35009765625 7.767333984375 51.646728515625 7.767333984375 51.778564453125 7.415771484375"

    data = getBundeslandContainsXMLQuery("bundeslaender", "geom", SAMPLE_NRW)
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)
    return json.loads(r.text)


def overlappingPolygons():
    SAMPLE_OVERLAP = "52.138742 12.275731 52.138329 12.288587 52.132832 12.279584 52.138742 12.275731"

    data = getOverlapXMLQuery("nettoflaechen", "geom", SAMPLE_OVERLAP)
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Basic {AUTH}'}
    r = requests.post(BASE_URL, data=data, headers=headers)
    return json.loads(r.text)
