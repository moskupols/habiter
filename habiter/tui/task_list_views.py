import itertools
import urwid
from habiter.models.list_model import MappingListProxyModel, FilterListProxyModel
from habiter.settings import ACCEL_TOGGLE_LIST_MODE
from habiter.tui.task_widgets import HabitWidget, DailyWidget, TodoWidget, RewardWidget


class TaskListView(urwid.LineBox):
    no_filter = (lambda wid: True, 'all')

    def __init__(self, title, tasks, widget_cls, filters=(no_filter,)):
        # TODO: filters should be task filters, not some widget filters.
        # it'll help to generalize TaskListView as a subclass of ListView

        self.title = title

        self.widget_list_model = FilterListProxyModel(
            MappingListProxyModel(tasks, widget_cls),
            filter_=self.no_filter[0],
            cls=urwid.SimpleListWalker)

        super().__init__(urwid.ListBox(self.widget_list_model.list), title=title)

        self.filters_list = filters
        self.filters_ring = itertools.cycle(filters)
        self.cur_filter = None
        self.switch_to_next_filter()

    def switch_to_next_filter(self):
        self.cur_filter = next(self.filters_ring)
        self.set_title('{} ({})'.format(self.title, self.cur_filter[1]))
        self.widget_list_model.set_filter(self.cur_filter[0])

    def keypress(self, size, key):
        if key in ACCEL_TOGGLE_LIST_MODE:
            self.switch_to_next_filter()
        else:
            return super().keypress(size, key)


class HabitListView(TaskListView):
    def __init__(self, user):
        super().__init__('Habits', user.habits, HabitWidget)


class DailyListView(TaskListView):
    def __init__(self, user):
        super().__init__(
            'Dailies',
            user.dailies, DailyWidget,
            (self.no_filter,
             (lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'checked')
             )
        )


class TodoListView(TaskListView):
    def __init__(self, user):
        super().__init__(
            "To-dos",
            user.todos, TodoWidget,
            ((lambda wid: not wid.get_state(), 'due'),
             (lambda wid: wid.get_state(), 'done')
             )
        )


class RewardListView(TaskListView):
    def __init__(self, user):
        super().__init__('Rewards', user.rewards, RewardWidget)
