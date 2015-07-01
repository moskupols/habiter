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


class TaskWidgetMixin:
    def __init__(self, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task


class HabitWidget(TaskWidgetMixin, urwid.SelectableIcon):
    def __init__(self, habit):
        super().__init__(habit, text=habit.text)
        self.habit = habit


class DailyWidget(TaskWidgetMixin, urwid.CheckBox):
    def __init__(self, daily):
        super().__init__(daily, label=daily.text, state=daily.completed)
        self.daily = daily


class TodoWidget(TaskWidgetMixin, urwid.CheckBox):
    def __init__(self, todo):
        super().__init__(todo, label=todo.text, state=todo.completed)
        self.todo = todo


class RewardWidget(TaskWidgetMixin, urwid.Button):
    def __init__(self, reward):
        super().__init__(reward, label=reward.text)
        self.reward = reward


class TaskListView(urwid.ListBox):
    def __init__(self, task_views):
        super().__init__(urwid.SimpleFocusListWalker(task_views))


class TasksView(urwid.Columns):
    def __init__(self, user):
        self.user = user
        lists = [
            TaskListView([HabitWidget(task) for task in user.habits]),
            TaskListView([DailyWidget(task) for task in user.dailies]),
            TaskListView([TodoWidget(task) for task in user.todos]),
            TaskListView([RewardWidget(task) for task in user.rewards])
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
