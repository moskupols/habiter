import itertools
import urwid
from habiter.models.list_model import MappingListProxyModel, FilterListProxyModel
from habiter.settings import ACCEL_NEXT_LIST_FILTER
from habiter.tui.task_widgets import HabitWidget, DailyWidget, TodoWidget, RewardWidget


class FilterListView(urwid.LineBox):
    no_filter = (lambda wid: True, 'all')

    TITLE_FORMAT = '{title} ({filter})'
    _compose_title = staticmethod(TITLE_FORMAT.format)

    list_title = 'Tasks'
    widget_cls = None
    task_filters = (no_filter,)

    def __init__(self, tasks):
        self.filters_ring = itertools.cycle(self.task_filters)
        self.cur_filter = next(self.filters_ring)

        self.filter_model = FilterListProxyModel(tasks, self.cur_filter[0])

        self.widget_list_model = MappingListProxyModel(
            self.filter_model, self.widget_cls, cls=urwid.SimpleListWalker)

        super().__init__(
            urwid.ListBox(self.widget_list_model.list),
            title=self._compose_title(title=self.list_title, filter=self.cur_filter[1]))

    def switch_to_next_filter(self):
        self.cur_filter = next(self.filters_ring)
        self.set_title(self._compose_title(title=self.list_title, filter=self.cur_filter[1]))
        self.filter_model.set_filter(self.cur_filter[0])

    def keypress(self, size, key):
        if key in ACCEL_NEXT_LIST_FILTER:
            self.switch_to_next_filter()
        else:
            return super().keypress(size, key)


class HabitListView(FilterListView):
    list_title = 'Habits'
    widget_cls = HabitWidget

    def __init__(self, user):
        super().__init__(user.habits)


class DailyListView(FilterListView):
    list_title = 'Dailies'
    widget_cls = DailyWidget
    task_filters = (
        FilterListView.no_filter,
        (lambda daily: not daily.completed, 'due'),
        (lambda daily: daily.completed, 'checked')
    )

    def __init__(self, user):
        super().__init__(user.dailies)


class TodoListView(FilterListView):
    list_title = 'To-dos'
    widget_cls = TodoWidget
    task_filters = (
        (lambda todo: not todo.completed, 'due'),
        (lambda todo: todo.completed, 'done')
    )

    def __init__(self, user):
        super().__init__(user.todos)


class RewardListView(FilterListView):
    list_title = 'Rewards'
    widget_cls = RewardWidget

    def __init__(self, user):
        super().__init__(user.rewards)
