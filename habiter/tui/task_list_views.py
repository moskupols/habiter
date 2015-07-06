from habiter.tui.list_views import AbstractFilterListView, AbstractListView
from habiter.tui.task_widgets import HabitWidget, DailyWidget, TodoWidget, RewardWidget


class HabitListView(AbstractListView):
    list_title = 'Habits'
    widget_cls = HabitWidget

    def __init__(self, user):
        super().__init__(user.habits)


class DailyListView(AbstractFilterListView):
    list_title = 'Dailies'
    widget_cls = DailyWidget
    task_filters = (
        AbstractFilterListView.no_filter,
        (lambda daily: not daily.completed, 'due'),
        (lambda daily: daily.completed, 'checked')
    )

    def __init__(self, user):
        super().__init__(user.dailies)


class TodoListView(AbstractFilterListView):
    list_title = 'To-dos'
    widget_cls = TodoWidget
    task_filters = (
        (lambda todo: not todo.completed, 'due'),
        (lambda todo: todo.completed, 'done')
    )

    def __init__(self, user):
        super().__init__(user.todos)


class RewardListView(AbstractListView):
    list_title = 'Rewards'
    widget_cls = RewardWidget

    def __init__(self, user):
        super().__init__(user.rewards)
