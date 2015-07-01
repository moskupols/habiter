import itertools

__author__ = 'moskupols'

from habiter import habit_api, models
from habiter.settings import user_id, api_key, ACCEL_QUIT, ACCEL_TOGGLE_LIST_MODE
import urwid


class UserInfoBar(urwid.Text):
    def __init__(self, user):
        super().__init__(user.name, align=urwid.CENTER, wrap=urwid.CLIP)


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
    no_filter = (lambda wid: True, 'all')

    def __init__(self, task_wids, wid_filters=(no_filter,)):
        super().__init__(urwid.SimpleFocusListWalker([]))
        self.all_task_wids = task_wids
        self.filters_ring = itertools.cycle(wid_filters)
        self.switch_to_next_filter()

    def update_view(self, task_wids, wid_filter):
        self.body.clear()
        self.body.extend([wid for wid in task_wids if wid_filter(wid)])

    def switch_to_next_filter(self):
        self.update_view(self.all_task_wids, next(self.filters_ring)[0])

    def keypress(self, size, key):
        if key in ACCEL_TOGGLE_LIST_MODE:
            self.switch_to_next_filter()
        else:
            return super().keypress(size, key)


class HabitListView(TaskListView):
    def __init__(self, tasks):
        super().__init__([HabitWidget(task) for task in tasks])


class DailyListView(TaskListView):
    def __init__(self, tasks):
        super().__init__(
            [DailyWidget(task) for task in tasks],
            (TaskListView.no_filter,
             (lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'checked')
             )
        )


class TodoListView(TaskListView):
    def __init__(self, todos):
        super().__init__(
            [TodoWidget(todo) for todo in todos if not todo.completed],
            ((lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'done'))
        )


class RewardListView(TaskListView):
    def __init__(self, tasks):
        super().__init__([RewardWidget(task) for task in tasks])


class TasksView(urwid.Columns):
    def __init__(self, user):
        self.user = user
        lists = (
            HabitListView(user.habits),
            DailyListView(user.dailies),
            TodoListView(user.todos),
            RewardListView(user.rewards)
        )
        self.habit_list, self.daily_list, self.todo_list, self.reward_list = lists
        super().__init__(lists, dividechars=3, min_width=20)


class MainFrame(urwid.Frame):
    def __init__(self, user):
        super().__init__(header=UserInfoBar(user), body=TasksView(user), footer=StatusBar())
        self.user = user

    def keypress(self, size, key):
        if key in ACCEL_QUIT:
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
