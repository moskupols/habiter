import itertools
import urwid
from habiter.habit_api import AuthorizedHabitAPI
from habiter.models.list_model import ListModel
from habiter.models.tasks import Habit, Daily, Todo, Reward, TASK_TYPES, TASK_CLASSES
from habiter.utils import signalling


@signalling(['profile_update', 'stats_update', 'tmp_effect'])
class User:
    def __init__(self, api: AuthorizedHabitAPI, synchronizer):
        self.api = api
        self.synchronizer = synchronizer

        self._data = {}

        self._task_lists = {type_: ListModel() for type_ in TASK_TYPES}

    def _reset_data(self, new_data):
        new_data = new_data or {}
        for k in ('profile', 'stats'):
            self._data[k] = new_data.get(k)
            urwid.emit_signal(self, k + '_update')

        for cls in TASK_CLASSES:
            self._task_lists[cls.type][:] = list(map(cls, new_data[cls.USER_ENTRY], itertools.repeat(self)))

    def pull(self):
        deferred = self.api.get_user()
        deferred.chain_action(self._reset_data, prev_result=True)
        self.synchronizer.add_call(deferred)

    def receive_delta(self, delta_data):
        stats_update = {k: delta_data[k] for k in ('lvl', 'gp', 'exp', 'mp', 'hp')}
        self._data.setdefault('stats', {}).update(stats_update)
        urwid.emit_signal(self, 'stats_update')
        if len(delta_data['_tmp']):
            urwid.emit_signal(self, 'tmp_effect', delta_data['_tmp'])

    @property
    def data(self)->dict:
        return self._data

    @property
    def name(self)->str:
        return self.data.get('profile', {}).get('name')

    class Stats:
        def __init__(self, level, gold, exp, mp, hp, max_exp, max_hp, max_mp):
            self.level = level
            self.gold = gold
            self.exp = exp
            self.mp = mp
            self.hp = hp
            self.max_exp = max_exp
            self.max_hp = max_hp
            self.max_mp = max_mp

    @property
    def stats(self):
        json = self.data.get('stats')
        if not json:
            return None
        return self.Stats(
            *map(json.get, ('lvl', 'gp', 'exp', 'mp', 'hp', 'toNextLevel', 'maxHealth', 'maxMP')))

    @property
    def habits(self):
        return self._task_lists[Habit.type]

    @property
    def dailies(self):
        return self._task_lists[Daily.type]

    @property
    def todos(self):
        return self._task_lists[Todo.type]

    @property
    def rewards(self):
        return self._task_lists[Reward.type]
