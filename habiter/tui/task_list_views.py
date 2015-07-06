import itertools
import urwid
from habiter.models.list_model import MappingListModelProxy
from habiter.settings import ACCEL_TOGGLE_LIST_MODE
from habiter.tui.task_widgets import HabitWidget, DailyWidget, TodoWidget, RewardWidget


class TaskListView(urwid.LineBox):
    no_filter = (lambda wid: True, 'all')

    def __init__(self, title, tasks, widget_cls, filters=(no_filter,)):
        self.widget_list_model = \
            MappingListModelProxy(tasks, widget_cls, cls=urwid.SimpleListWalker)

        super().__init__(urwid.ListBox(self.widget_list_model.list), title=title)

        self.title = title

        self.filters_list = filters
        self.filters_ring = itertools.cycle(filters)
        self.cur_filter = next(self.filters_ring)

    def _update_view(self, task_wids, wid_filter):
        # new_title = self.title
        # if len(self.filters_list) > 1:
        #     new_title += '(' + wid_filter[1] + ')'
        # self.set_title(new_title)
        # self.list_box.body[:] = [wid for wid in task_wids if wid_filter[0](wid)]
        pass

    def switch_to_next_filter(self):
        self.cur_filter = next(self.filters_ring)
        self._update_view(self.all_task_wids, self.cur_filter)

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
