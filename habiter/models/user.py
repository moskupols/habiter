from collections import OrderedDict, ChainMap
import urwid
from habiter.habit_api import AuthorizedHabitAPI
from habiter.models.tasks import Habit, Daily, Todo, Reward, Task
from habiter.utils import signalling


@signalling(['reset', 'stats_update', 'tmp_effect'])
class User:
    def __init__(self, api: AuthorizedHabitAPI, synchronizer):
        self.api = api
        self.synchronizer = synchronizer

        self._data = {}

        self._habits = OrderedDict()
        self._dailies = OrderedDict()
        self._todos = OrderedDict()
        self._rewards = OrderedDict()

        self._tasks_dicts = {
            Habit.USER_ENTRY: self._habits,
            Habit.type: self._habits,
            Daily.USER_ENTRY: self._dailies,
            Daily.type: self._dailies,
            Todo.USER_ENTRY: self._todos,
            Todo.type: self._todos,
            Reward.USER_ENTRY: self._rewards,
            Reward.type: self._rewards
        }

        self._tasks = ChainMap(self._habits, self._dailies, self._todos, self._rewards)

    def _bind_task(self, task):
        assert task.id not in self._tasks
        urwid.connect_signal(task, 'update', self._update_task_data, weak_args=(task,))
        self._tasks_dicts[task.type][task.id] = task

    def _unbind_task(self, task):
        assert task.id in self._tasks
        urwid.disconnect_signal(task, 'update', self._update_task_data, weak_args=(task,))
        self._tasks_dicts[task.type].pop(task.id)

    def _make_task_for_data(self, data):
        for cls in (Habit, Daily, Todo, Reward):
            if cls.type == data.get('type'):
                return cls(id_or_data=data, user=self)
        assert False, 'unknown task type "{}"'.format(data.get('type'))

    def _update_task_data(self, new_task: Task):
        assert new_task.user is self
        for i, t in enumerate(self._data[new_task.USER_ENTRY]):
            if t['id'] == new_task.id:
                self._data[new_task.USER_ENTRY][i] = new_task.data
                break

    def get_task(self, task_id):
        return self._tasks.get(task_id)

    def _reset_data(self, new_data):
        # TODO: proper update
        self._todos.clear()
        self._dailies.clear()
        self._rewards.clear()
        self._habits.clear()

        self._data = new_data
        if new_data:
            for cls in (Habit, Daily, Todo, Reward):
                for task_data in new_data[cls.USER_ENTRY]:
                    self._bind_task(self._make_task_for_data(task_data))

        urwid.emit_signal(self, 'reset')

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
        return self._habits.values()

    @property
    def dailies(self):
        return self._dailies.values()

    @property
    def todos(self):
        return self._todos.values()

    @property
    def rewards(self):
        return self._rewards.values()
