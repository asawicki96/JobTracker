import requests
import json
from django.conf import settings
import typing as t

JSON = t.Union[str, int, float, bool, None, t.Mapping[str, 'JSON'], t.List['JSON']]

""" Connect Joobe REST API when dict of strings given and returns JSON object,
    params: query dict """

def jooble_conn(query: dict) -> JSON:
    host = 'http://pl.jooble.org'
    api_key = settings.JOOBLE_API_KEY
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    data = json.dumps(query)

    response = requests.post(host+'/api/'+api_key, data=data, verify=True, headers=headers)
    status = response.status_code

    if response.status_code != 200:
        print('Status:', status, 'Problem with the request. Exiting.')
        exit()
    return response.json()

    """ Converts all values in given query dict to string and calls jooble_conn function """

def get_jooble_jobs(params: dict) -> JSON:
    query = {}

    if not 'page' in params.keys():
        query['page'] = 1

    for key, value in params.items():
        query[key] = str(value)

    return jooble_conn(query)

#print(get_jooble_jobs({'keywords': 'python', 'page': 2}))




