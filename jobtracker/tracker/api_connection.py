import requests
import json
from django.conf import settings


def jooble_conn(query: dict):
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


def get_jooble_jobs(params: dict):
    query = {}

    if not 'page' in params.keys():
        query['page'] = 1

    for key, value in params.items():
        query[key] = str(value)

    return jooble_conn(query)

#print(get_jooble_jobs({'keywords': 'python', 'page': 2}))




