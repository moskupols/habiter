import urwid
from habiter.utils import signalling


class Task:
    """
    Task model.
    See https://github.com/HabitRPG/habitrpg/blob/develop/website/src/models/task.js
    """

    HABIT = 'habit'
    DAILY = 'daily'
    TODO = 'todo'
    REWARD = 'reward'

    USER_ENTRY = None  # should be filled by subclass, p.e. 'habits'

    def __init__(self, id_or_data, user: 'User'):
        self.user = user
        self._data = {}
        self._id = None

        if id_or_data is not None:
            if isinstance(id_or_data, dict):
                self.update_data(id_or_data, sync=False)
            else:
                self._id = id_or_data

    def _update_data(self, data: dict):
        self._data.update(data)

        self._id = self._id or self.data.get('id')
        assert not self._id or self._id == self.data.get('id')

        t = self.data.get('type')
        assert not t or t == self.type

        urwid.emit_signal(self, 'update')

    def receive_delta(self, delta_data):
        d_value = delta_data['delta']
        assumption = (1 if d_value > 0 else -1)
        self._update_data({'value': self.value + d_value - assumption})
        self.user.receive_delta(delta_data)
        return delta_data

    def update_data(self, data: dict, sync=True):
        self._update_data(data)
        if sync:
            assert self.user
            data.setdefault('id', self.id)
            deferred = self.user.api.update_task(data).chain_action(self._update_data)
            self.user.synchronizer.add_call(deferred)

    def pull(self):
        assert self.user
        deferred = self.user.api.get_task().chain_action(self._update_data)
        self.user.synchronizer.add_call(deferred)

    def _score(self, direction: '"up" | "down"'):
        assert direction in ('up', 'down')
        assert self.user
        self._update_data({'value': self._data['value'] + (1 if direction == 'up' else -1)})
        deferred = self.user.api.score_task(self, direction)\
            .chain_action(self.receive_delta)
        self.user.synchronizer.add_call(deferred)

    @property
    def data(self) ->dict:
        return self._data

    @property
    def id(self) ->str:
        return self._id

    @property
    def text(self) ->str:
        return self.data.get('text')

    @property
    def value(self) ->float:
        return self.data.get('value')

    def __str__(self):
        return self.text or self.id


@signalling(['update'])
class Habit(Task):
    type = Task.HABIT
    USER_ENTRY = 'habits'

    @property
    def up_available(self) ->bool:
        return self.data.get('up')

    @property
    def down_available(self) ->bool:
        return self.data.get('down')

    def score(self, direction: '"up" | "down"'):
        if direction == 'up' and not self.up_available:
            return
        if direction == 'down' and not self.down_available:
            return
        self._score(direction)


class CompletableTask(Task):
    @property
    def completed(self) ->bool:
        return self.data.get('completed')

    @completed.setter
    def completed(self, new_state):
        if new_state != self.completed:
            self.data['completed'] = new_state
            # we shouldn't issue sync call here, because it will be done by super with value change
            self._score(('down', 'up')[new_state])


@signalling(['update'])
class Daily(CompletableTask):
    type = Task.DAILY
    USER_ENTRY = 'dailys'  # yeah

    @property
    def streak(self) ->int:
        return self.data.get('streak')


@signalling(['update'])
class Todo(CompletableTask):
    type = Task.TODO
    USER_ENTRY = 'todos'


@signalling(['update'])
class Reward(Task):
    type = Task.REWARD
    USER_ENTRY = 'rewards'

TASK_CLASSES = (Habit, Daily, Todo, Reward)
TASK_TYPES = tuple(cls.type for cls in TASK_CLASSES)
