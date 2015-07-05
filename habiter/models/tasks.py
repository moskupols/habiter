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


@signalling(['update'])
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


@signalling(['update'])
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


@signalling(['update'])
class Todo(Task):
    type = Task.TODO
    USER_ENTRY = 'todos'

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)

    @property
    def completed(self)->bool:
        return self.data.get('completed')


@signalling(['update'])
class Reward(Task):
    type = Task.REWARD
    USER_ENTRY = 'rewards'

    def __init__(self, user, id_or_data=None):
        super().__init__(user, id_or_data)
