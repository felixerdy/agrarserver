from requests import get
from flask import request, Response
import os

GEOSERVER_HOST = os.getenv('GEOSERVER_HOST', "localhost")
GEOSERVER_PORT = os.getenv('GEOSERVER_PORT', '8080')


BASE_URL = f'http://{GEOSERVER_HOST}:{GEOSERVER_PORT}/geoserver/felix/wms?'


def read():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """
    r = get(BASE_URL, params=request.args, headers=request.headers)

    return Response(r, content_type="image/png")
