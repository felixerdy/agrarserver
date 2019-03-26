from requests import get

BASE_URL = 'http://localhost:8080/geoserver/felix/ows?'
WFS_TYPE_NAME = 'felix:bundeslaender'
WFS_QUERY = f'service=WFS&version=1.0.0&request=GetFeature&typeName={WFS_TYPE_NAME}&outputFormat=application/json'


def read():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """

    return get(f'{BASE_URL}{WFS_QUERY}').json()
