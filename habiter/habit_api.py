import requests

__author__ = 'moskupols'


class HabitAPIException(Exception):
    pass


class HabitAPIUnavailableException(HabitAPIException):
    pass


class HabitAPI:

    URL_INTERFIX = '/api/v2/'

    def __init__(self, user_id, api_key, base_url='https://habitrpg.com'):
        self.user_id = user_id
        self.api_key = api_key
        self.base_url = base_url

    def request(self, method, path, headers=None, **parameters)->dict:
        url = self.base_url + self.URL_INTERFIX + path

        if headers is None:
            headers = dict()
        headers.setdefault('x-api-user', self.user_id)
        headers.setdefault('x-api-key', self.api_key)
        headers.setdefault('Content-Type', 'application/json')

        response = requests.request(method, url, parameters=parameters, headers=headers)
        if response.ok:
            return response.json()
        if response.status_code >= 500:
            raise HabitAPIUnavailableException(response.reason)
        try:
            json = response.json()
        except Exception as e:
            raise HabitAPIException('Api broken: ' + str(e))
        raise HabitAPIException(json['err'])

    def status(self)->bool:
        result = self.request('get', 'status')
        return result['status'] == 'up'
