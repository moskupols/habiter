from collections import ChainMap, OrderedDict
import urwid

from habiter.habit_api import AuthorizedHabitAPI
from habiter.utils import signalling


@signalling(['update'])
class Task:
    """
    Task model.
    See https://github.com/HabitRPG/habitrpg/blob/develop/website/src/models/task.js
    """

    HABIT = 'habit'
    DAILY = 'daily'
    TODO = 'todo'
    REWARD = 'reward'

    def __init__(self, user: 'User', id_or_data):
        self.user = user
        self._data = {}
        self._id = None

        if id_or_data is not None:
            if isinstance(id_or_data, dict):
                self.update_data(id_or_data, sync=False)
            else:
                self._id = id_or_data

    def update_data(self, data: dict, sync=True):
        self._data.update(data)
        self._id = self.data.get('id')

        t = self.data.get('type')
        assert not t or t == self.type

        urwid.emit_signal(self, 'update')

        if sync:
            # TODO sync
            pass

    def pull(self):
        raise NotImplementedError

    @property
    def data(self)->dict:
        return self._data

    @property
    def id(self)->str:
        return self._id

    @property
    def text(self)->str:
        return self.data.get('text')

    @property
    def value(self)->float:
        return self.data.get('value')


class Habit(Task):
    type = Task.HABIT
    USER_ENTRY = 'habits'

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)

    @property
    def up_available(self)->bool:
        return self.data.get('up')

    @property
    def down_available(self)->bool:
        return self.data.get('down')


class Daily(Task):
    type = Task.DAILY
    USER_ENTRY = 'dailys'  # yeah

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)

    @property
    def completed(self)->bool:
        return self.data.get('completed')

    @property
    def streak(self)->int:
        return self.data.get('streak')


class Todo(Task):
    type = Task.TODO
    USER_ENTRY = 'todos'

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)

    @property
    def completed(self)->bool:
        return self.data.get('completed')


class Reward(Task):
    type = Task.REWARD
    USER_ENTRY = 'rewards'

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)


@signalling(['reset'])
class User:
    def __init__(self, api: AuthorizedHabitAPI, synchronizer=None):
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

    def _task_for_data(self, data):
        for cls in (Habit, Daily, Todo, Reward):
            if cls.type == data.get('type'):
                return cls(self, data)
        assert False, 'unknown task type "{}"'.format(data.get('type'))

    def _update_task_data(self, new_task: Task):
        assert new_task.user is self
        self._data[new_task.USER_ENTRY][new_task.id] = new_task.data

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
                    self._bind_task(self._task_for_data(task_data))

        urwid.emit_signal(self, 'reset')

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
        return self._habits.items()

    @property
    def dailies(self):
        return self._dailies.items()

    @property
    def todos(self):
        return self._todos.items()

    @property
    def rewards(self):
        return self._rewards.items()
