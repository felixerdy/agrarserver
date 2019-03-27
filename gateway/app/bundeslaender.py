from requests import get
import os

GEOSERVER_HOST = os.getenv('GEOSERVER_HOST', "localhost")
GEOSERVER_PORT = os.getenv('GEOSERVER_PORT', "8080")

BASE_URL = f'http://{GEOSERVER_HOST}:{GEOSERVER_PORT}/geoserver/felix/ows?'
WFS_TYPE_NAME = 'felix:bundeslaender'
WFS_QUERY = f'service=WFS&version=1.0.0&request=GetFeature&typeName={WFS_TYPE_NAME}&outputFormat=application/json'


def read():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """

    return get(f'{BASE_URL}{WFS_QUERY}').json()
