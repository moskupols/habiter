import itertools
import urwid

from habiter import habit_api, models
from habiter.settings import (
    USER_ID, API_KEY,
    ACCEL_QUIT, ACCEL_TOGGLE_LIST_MODE,
    VALUE_COLOR_BOUNDS, PALETTE, RESET_TERMINAL_PALETTE,
)


class UserInfoBar(urwid.Text):
    PARTS = (
        ('name',  '{u.name}'),
        ('level', '{s.level} level'),
        ('hp',    '{s.hp}/{s.max_hp} hp'),
        ('exp',   '{s.exp}/{s.max_exp} exp'),
        ('mp',    '{s.mp}/{s.max_mp} mp'),
        ('gold',  '{s.gold:.2f} gold'),
    )

    @classmethod
    def info_markup_for(cls, user):
        def intersperse(lst, sep):
            seps = [sep] * (len(lst) * 2 - 1)
            seps[0::2] = lst
            return seps

        markup = [(part, form.format(u=user, s=user.stats)) for part, form in cls.PARTS]
        markup = intersperse(markup, ', ')
        markup = ('info_bar', markup)
        return markup

    def __init__(self, user):
        super().__init__(self.info_markup_for(user), align=urwid.CENTER)


class StatusBar(urwid.Text):
    def __init__(self, markup='initial status'):
        super().__init__(markup, wrap=urwid.CLIP)


class TaskWidgetMixin:
    def __init__(self, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task

    @classmethod
    def value_attr(cls, task):
        v = task.value
        bounds = sorted(VALUE_COLOR_BOUNDS)
        segments = list(zip(bounds[:-1], bounds[1:]))
        for l, r in segments:
            if l <= v < r:
                return 'task-value_{}_{}'.format(l, r)
        if v < bounds[0]:
            return 'task-value_' + str(bounds[0])
        return 'task-value_' + str(bounds[-1])

    @classmethod
    def value_markup(cls, task):
        return cls.value_attr(task), '[{}]'.format(round(task.value))


class HabitWidget(TaskWidgetMixin, urwid.SelectableIcon):
    @classmethod
    def markup_for(cls, habit):
        plus_minus = '?-+±'[habit.down_available + habit.up_available * 2]
        return [
            ('habit-plus_minus', plus_minus), ' ',
            cls.value_markup(habit), ' ',
            ('task-text', habit.text),
        ]

    def __init__(self, habit):
        super().__init__(habit, text=self.markup_for(habit))
        self.habit = habit


class DailyWidget(TaskWidgetMixin, urwid.CheckBox):
    @classmethod
    def label_for(cls, daily):
        return [
            cls.value_markup(daily),
            ('daily-streak', '[{}] '.format(daily.streak)) if daily.streak else ' ',
            ('task-text', daily.text),
        ]

    def __init__(self, daily):
        super().__init__(daily, label=self.label_for(daily), state=daily.completed)
        self.daily = daily


class TodoWidget(TaskWidgetMixin, urwid.CheckBox):
    @classmethod
    def label_for(cls, todo):
        return [
            cls.value_markup(todo),
            ('task-text', todo.text),
        ]

    def __init__(self, todo):
        super().__init__(todo, label=self.label_for(todo), state=todo.completed)
        self.todo = todo


class RewardWidget(TaskWidgetMixin, urwid.Button):
    @classmethod
    def markup_for(cls, reward):
        return [
            ('gold', '({r.value})'.format(r=reward)), ' ',
            ('task-text', reward.text),
        ]

    def __init__(self, reward):
        super().__init__(reward, label=self.markup_for(reward))
        self.reward = reward


class TaskListView(urwid.LineBox):
    no_filter = (lambda wid: True, 'all')

    def __init__(self, title, task_wids, filters=(no_filter,)):
        self.list_box = urwid.ListBox(urwid.SimpleFocusListWalker([]))
        super().__init__(self.list_box, title=title)

        self.title = title
        self.all_task_wids = task_wids
        self.filters_list = filters
        self.filters_ring = itertools.cycle(filters)
        self.switch_to_next_filter()

    def update_view(self, task_wids, wid_filter):
        new_title = self.title
        if len(self.filters_list) > 1:
            new_title += '(' + wid_filter[1] + ')'
        self.set_title(new_title)
        self.list_box.body[:] = [wid for wid in task_wids if wid_filter[0](wid)]

    def switch_to_next_filter(self):
        self.update_view(self.all_task_wids, next(self.filters_ring))

    def keypress(self, size, key):
        if key in ACCEL_TOGGLE_LIST_MODE:
            self.switch_to_next_filter()
        else:
            return super().keypress(size, key)


class HabitListView(TaskListView):
    def __init__(self, tasks):
        super().__init__('Habits', [HabitWidget(task) for task in tasks])


class DailyListView(TaskListView):
    def __init__(self, tasks):
        super().__init__(
            'Dailies',
            [DailyWidget(task) for task in tasks],
            (self.no_filter,
             (lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'checked')
             )
        )


class TodoListView(TaskListView):
    def __init__(self, todos):
        super().__init__(
            "To-dos",
            [TodoWidget(todo) for todo in todos],
            ((lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'done')
             )
        )


class RewardListView(TaskListView):
    def __init__(self, tasks):
        super().__init__('Rewards', [RewardWidget(task) for task in tasks])


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
        super().__init__(lists, dividechars=0, min_width=20)


class MainFrame(urwid.Frame):
    def __init__(self, user):
        super().__init__(header=UserInfoBar(user), body=TasksView(user), footer=StatusBar())
        self._command_map['j'] = self._command_map['down']
        self._command_map['k'] = self._command_map['up']
        self._command_map['h'] = self._command_map['left']
        self._command_map['l'] = self._command_map['right']

        self.user = user

    def keypress(self, size, key):
        if key in ACCEL_QUIT:
            raise urwid.ExitMainLoop()
        return super().keypress(size, key)


def run():
    api = habit_api.HabitAPI(USER_ID, API_KEY)
    user = models.User(api)

    # user = Mock()
    # user.name = 'mocked name'

    main = MainFrame(user)

    loop = urwid.MainLoop(main, palette=PALETTE, handle_mouse=False)
    if RESET_TERMINAL_PALETTE:
        loop.screen.reset_default_terminal_palette()

    loop.run()
