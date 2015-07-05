from functools import update_wrapper
import requests
from habiter.habit_api.api_call import DeferredAPICallFactory, DeferredAPICall

DEFAULT_API_URL = 'https://habitrpg.com/api/v2/'
DEFAULT_TIMEOUT = 5


def _api_call_description(foo):
    def _make_deferred_call(self, *args, errback=None, err_args=(), **kwargs):
        return self.call_factory.request(
            errback=errback, err_args=err_args, **foo(self, *args, **kwargs))
    return update_wrapper(_make_deferred_call, foo)


class HabitAPI:
    def __init__(self, api_url=None, timeout=None, call_factory_factory=DeferredAPICallFactory):
        if api_url is None:
            api_url = DEFAULT_API_URL
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.call_factory = call_factory_factory(self.session, timeout=timeout, api_base_url=api_url)

    @_api_call_description
    def status(self)->DeferredAPICall:
        return {
            'method': 'get',
            'path': 'status',
            'postproc': lambda json: json['ok'],
            'description': 'ping server for its status',
        }

    @_api_call_description
    def content(self)->DeferredAPICall:
        return {
            'method': 'get',
            'path': 'content',
            'description': 'load all text assets',
        }


def _get_id(task_or_id):
    if isinstance(task_or_id, str):
        return task_or_id
    return task_or_id.id


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
    def get_user(self)->DeferredAPICall:
        return {
            'method': 'get',
            'path': 'user',
            'description': 'load entire user document',
        }

    @_api_call_description
    def toggle_sleep(self)->DeferredAPICall:
        return {
            'method': 'post',
            'path': 'user/sleep',
            'description': 'toggle sleep',
        }

    @_api_call_description
    def rebirth(self)->DeferredAPICall:
        return {
            'method': 'post',
            'path': 'user/rebirth',
            'description': 'rebirth',
        }

    @_api_call_description
    def get_tasks(self)->DeferredAPICall:
        return {
            'method': 'get',
            'path': 'user/tasks',
            'description': 'load all tasks',
        }

    @_api_call_description
    def get_task(self, task_or_id)->DeferredAPICall:
        return {
            'method': 'get',
            'path': 'user/tasks/' + _get_id(task_or_id),
            'description': 'load task "{!s}"'.format(task_or_id),
        }

    @_api_call_description
    def new_task(self, task_data: dict)->DeferredAPICall:
        return {
            'method': 'post',
            'path': 'user/tasks/' + task_data['id'],
            'body': task_data,
            'description': 'create new task "{}"'.format(task_data['text']),
        }

    @_api_call_description
    def update_task(self, task_data: dict)->DeferredAPICall:
        return {
            'method': 'put',
            'path': 'user/tasks/' + task_data['id'],
            'body': task_data,
            'description': 'update task "{}"'.format(task_data['text']),
        }

    @_api_call_description
    def delete_task(self, task_or_id)->DeferredAPICall:
        return {
            'method': 'delete',
            'path': 'user/tasks/' + _get_id(task_or_id),
            'description': 'delete task "{!s}"'.format(task_or_id),
        }

    @_api_call_description
    def score_task(self, task_or_id, direction='up')->DeferredAPICall:
        return {
            'method': 'post',
            'path': 'user/tasks/{id}/{dir}'.format(id=_get_id(task_or_id), dir=direction),
            'description': direction + 'score task "{!s}"'.format(task_or_id),
        }
