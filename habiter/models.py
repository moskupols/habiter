from habiter.habit_api import AuthorizedHabitAPI


class Task:
    """
    Task model.
    See https://github.com/HabitRPG/habitrpg/blob/develop/website/src/models/task.js
    """

    HABIT = 'habit'
    DAILY = 'daily'
    TODO = 'todo'
    REWARD = 'reward'

    def __init__(self, api: AuthorizedHabitAPI, id_or_data):
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
        self._data = self.api.get_task(self.id)()
        self._dirty = False

    @property
    def data(self):
        if self._data is None:
            self.pull()
        return self._data

    @property
    def id(self):
        return self._id

    @property
    def text(self)->str:
        return self.data['text']

    @property
    def type(self)->str:
        return self.data['type']

    @property
    def value(self)->float:
        return self.data['value']


class Habit(Task):
    TYPE = Task.HABIT
    PLURAL = 'habits'

    def __init__(self, api, id_or_data):
        super().__init__(api, id_or_data)
        if self._data is not None:
            assert self.type == Task.HABIT

    @property
    def up_available(self)->bool:
        return self.data['up']

    @property
    def down_available(self)->bool:
        return self.data['down']


class Daily(Task):
    TYPE = Task.DAILY
    PLURAL = 'dailys'  # yeah

    def __init__(self, api, id_or_data):
        super().__init__(api, id_or_data)
        if self._data is not None:
            assert self.type == Task.DAILY

    @property
    def completed(self)->bool:
        return self.data['completed']

    @property
    def streak(self)->int:
        return self.data['streak']


class Todo(Task):
    TYPE = Task.TODO
    PLURAL = 'todos'

    def __init__(self, api, id_or_data):
        super().__init__(api, id_or_data)
        if self._data is not None:
            assert self.type == Task.TODO

    @property
    def completed(self)->bool:
        return self.data['completed']


class Reward(Task):
    TYPE = Task.REWARD
    PLURAL = 'rewards'

    def __init__(self, api, id_or_data):
        super().__init__(api, id_or_data)
        if self._data is not None:
            assert self.type == Task.REWARD


class User:
    def __init__(self, api: AuthorizedHabitAPI):
        self.api = api
        self.pull()

    def _update_data(self, new_data):
        self._data = new_data

        def task_list(klass):
            return tuple(klass(self.api, task) for task in new_data[klass.PLURAL])
        self._habits = task_list(Habit)
        self._dailies = task_list(Daily)
        self._todos = task_list(Todo)
        self._rewards = task_list(Reward)

    def pull(self):
        new_data = self.api.get_user()()
        self._update_data(new_data)

    def pull_tasks(self):
        # for consistency of self._data we have to change it, and only then reload tasks.
        # probably later we'll make it better and less json-based

        new_tasks = self.api.get_tasks()()
        for klass in (Habit, Daily, Todo, Reward):
            self._data[klass.PLURAL] = [d for d in new_tasks if d['type'] == klass.TYPE]

        self._update_data(self._data)

    @property
    def data(self)->dict:
        return self._data

    @property
    def name(self)->str:
        return self.data['profile']['name']

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
        json = self.data['stats']
        return self.Stats(
            level=json['lvl'],
            gold=json['gp'],
            exp=json['exp'],
            mp=json['mp'],
            hp=json['hp'],
            max_exp=json['toNextLevel'],
            max_hp=json['maxHealth'],
            max_mp=json['maxMP'])

    @property
    def habits(self)->tuple:
        return self._habits

    @property
    def dailies(self)->tuple:
        return self._dailies

    @property
    def todos(self)->tuple:
        return self._todos

    @property
    def rewards(self)->tuple:
        return self._rewards
