import requests
from habiter.habit_api.operations import DelayedAPIRequestOperationFactory

DEFAULT_API_URL = 'https://habitrpg.com/api/v2/'
DEFAULT_TIMEOUT = 5


def _api_call_description(foo):
    def _make_delayed_request(self, callback=None, *args, **kwargs):
        return self.request_factory.request(callback=callback, **foo(self, *args, **kwargs))
    return _make_delayed_request


class HabitAPI:
    def __init__(self, api_url=None, timeout=None):
        if api_url is None:
            api_url = DEFAULT_API_URL
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.request_factory = DelayedAPIRequestOperationFactory(self.session, timeout=timeout, api_base_url=api_url)

    @_api_call_description
    def status(self):
        return {
            'method': 'get',
            'path': 'status',
            'postproc': lambda json: json['ok'],
            'description': 'ping server for its status',
        }

    @_api_call_description
    def content(self):
        return {
            'method': 'get',
            'path': 'content',
            'description': 'load all text assets',
        }


class AuthorizedHabitAPI(HabitAPI):
    def __init__(self, user_id, api_key, api_url=None, timeout=None):
        super().__init__(api_url=api_url, timeout=timeout)
        self.session.headers.update({
            'x-api-user': user_id,
            'x-api-key': api_key,
        })
        self.user_id = user_id
        self.api_key = api_key

    @_api_call_description
    def get_user(self):
        return {
            'method': 'get',
            'path': 'user',
            'description': 'load entire user document',
        }

    @_api_call_description
    def get_tasks(self):
        return {
            'method': 'get',
            'path': 'user/tasks',
            'description': 'load all tasks',
        }

    @_api_call_description
    def get_task(self, task_id):
        return {
            'method': 'get',
            'path': 'user/tasks/' + task_id,
            'description': 'load task with id ' + task_id,
        }