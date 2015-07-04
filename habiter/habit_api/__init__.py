from functools import update_wrapper
import requests
from habiter.habit_api.api_call import DelayedAPICallFactory

DEFAULT_API_URL = 'https://habitrpg.com/api/v2/'
DEFAULT_TIMEOUT = 5


def _api_call_description(foo):
    def _make_delayed_request(self, callback=None, exception_handler=None, *args, **kwargs):
        return self.call_factory.request(
            callback=callback, exception_handler=exception_handler, **foo(self, *args, **kwargs))
    return update_wrapper(_make_delayed_request, foo)


class HabitAPI:
    def __init__(self, api_url=None, timeout=None, call_factory_factory=DelayedAPICallFactory):
        if api_url is None:
            api_url = DEFAULT_API_URL
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.call_factory = call_factory_factory(self.session, timeout=timeout, api_base_url=api_url)

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
    def __init__(self, user_id, api_key, api_url=None, timeout=None, **kwargs):
        super().__init__(api_url=api_url, timeout=timeout, **kwargs)
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
    def toggle_sleep(self):
        return {
            'method': 'post',
            'path': 'user/sleep',
            'description': 'toggle sleep',
        }

    @_api_call_description
    def rebirth(self):
        return {
            'method': 'post',
            'path': 'user/rebirth',
            'description': 'rebirth',
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
            'description': 'load task ' + task_id,
        }

    @_api_call_description
    def new_task(self, task_data: dict):
        return {
            'method': 'post',
            'path': 'user/tasks/' + task_data['id'],
            'body': task_data,
            'description': 'create new task "{}"'.format(task_data['text']),
        }

    @_api_call_description
    def update_task(self, task_data: dict):
        return {
            'method': 'put',
            'path': 'user/tasks/' + task_data['id'],
            'body': task_data,
            'description': 'update task "{}"'.format(task_data['text']),
        }

    @_api_call_description
    def delete_task(self, task_data: dict):
        return {
            'method': 'delete',
            'path': 'user/tasks/' + task_data['id'],
            'body': task_data,
            'description': 'delete task "{}"'.format(task_data['text']),
        }

    @_api_call_description
    def score_task(self, task_id, direction='up'):
        return {
            'method': 'post',
            'path': 'user/tasks/{id}/{dir}'.format(id=task_id, dir=direction),
            'description': direction + 'score task ' + task_id,
        }
