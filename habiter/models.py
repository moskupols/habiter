__author__ = 'moskupols'

from .habit_api import HabitAPI


class Task:
    def __init__(self, api: HabitAPI, id_or_data):
        self.api = api
        self._dirty = False

        if isinstance(id_or_data, dict):
            self._data = id_or_data
            self._id = self._data['id']
        else:
            self._data = None
            self._id = id_or_data

    def pull(self):
        assert not self._dirty  # TODO: handle transactions better
        self._data = self.api.request('get', self.relative_url)
        self._dirty = False

    def push(self):
        if self._dirty:
            self.api.request('put', self.relative_url, object=self._data)
            self._dirty = False

    @property
    def relative_url(self):
        return 'user/tasks/' + self._id

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        if self._data is None:
            self.pull()
        return self._data

