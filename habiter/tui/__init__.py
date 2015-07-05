import urwid

from habiter.settings import ACCEL_QUIT, ACCEL_UPDATE_USER, ACCEL_SYNC_ONE
from habiter.tui.status_bar import StatusBar
from habiter.tui.task_list_views import HabitListView, DailyListView, TodoListView, RewardListView
from habiter.tui.user_info_bar import UserInfoBar


class TasksView(urwid.Columns):
    def __init__(self, user):
        self.user = user
        lists = (
            HabitListView(user),
            DailyListView(user),
            TodoListView(user),
            RewardListView(user)
        )
        self.habit_list, self.daily_list, self.todo_list, self.reward_list = lists
        super().__init__(lists, dividechars=0, min_width=20)


class MainFrame(urwid.Frame):
    def __init__(self, user):
        self.info_bar = UserInfoBar(user)
        self.tasks_view = TasksView(user)

        # due_deferred_view = urwid.ListBox(urwid.SimpleListWalker(user.synchronizer.due_calls))
        # done_deferred_view = urwid.ListBox(urwid.SimpleListWalker(user.synchronizer.done_calls))
        # deferred_views = urwid.Columns()

        self.status_bar = StatusBar()

        super().__init__(header=self.info_bar, body=self.tasks_view, footer=self.status_bar)

        self._command_map['j'] = self._command_map['down']
        self._command_map['k'] = self._command_map['up']
        self._command_map['h'] = self._command_map['left']
        self._command_map['l'] = self._command_map['right']

        self.user = user

    def keypress(self, size, key):
        self.get_footer().set_text(key)
        if key in ACCEL_QUIT:
            raise urwid.ExitMainLoop()
        if key in ACCEL_UPDATE_USER:
            self.user.pull()
        if key in ACCEL_SYNC_ONE:
            self.user.synchronizer.perform_one_call()
        return super().keypress(size, key)


