from unittest.mock import Mock

__author__ = 'moskupols'

from habiter import habit_api, models
from habiter.settings import user_id, api_key
import urwid


class UserInfoBar(urwid.Text):
    def __init__(self, user):
        super().__init__(user.name, wrap=urwid.CLIP)


class StatusBar(urwid.Text):
    def __init__(self, markup='initial status'):
        super().__init__(markup, wrap=urwid.CLIP)


class TaskView(urwid.Text):
    def __init__(self, task):
        super().__init__(task.text)
        self.task = task


class HabitView(TaskView):
    pass


class DailyView(TaskView):
    pass


class TodoView(TaskView):
    pass


class RewardView(TaskView):
    pass


class TaskListView(urwid.ListBox):
    def __init__(self, task_views):
        super().__init__(urwid.SimpleListWalker(task_views))


class TasksView(urwid.Columns):
    def __init__(self, user):
        self.user = user
        lists = [
            TaskListView([HabitView(task) for task in user.habits]),
            TaskListView([DailyView(task) for task in user.dailies]),
            TaskListView([TodoView(task) for task in user.todos]),
            TaskListView([RewardView(task) for task in user.rewards])
        ]
        super().__init__(lists, dividechars=3, min_width=20)


class MainFrame(urwid.Frame):
    def __init__(self, user):
        super().__init__(header=UserInfoBar(user), body=TasksView(user), footer=StatusBar())
        self.user = user

    def keypress(self, size, key):
        if key in 'qQ':
            raise urwid.ExitMainLoop()
        return super().keypress(size, key)


def run():
    api = habit_api.HabitAPI(user_id, api_key)
    user = models.User(api)

    # user = Mock()
    # user.name = 'mocked name'

    main = MainFrame(user)

    loop = urwid.MainLoop(main, handle_mouse=False)
    loop.run()
