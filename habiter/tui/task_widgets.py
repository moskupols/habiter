import urwid

from habiter.settings import VALUE_COLOR_BOUNDS, ACCEL_HABIT_PLUS, ACCEL_HABIT_MINUS, VALUE_ROUND


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
        return cls.value_attr(task), '[{}]'.format(round(task.value, VALUE_ROUND))

    @classmethod
    def text_attr(cls):
        return 'task-text'

    @classmethod
    def text_markup(cls, task):
        return cls.text_attr(), task.text

    @classmethod
    def task_markup(cls, task):
        return [
            cls.value_markup(task), ' ',
            cls.text_markup(task),
        ]


class HabitWidget(TaskWidgetMixin, urwid.SelectableIcon):
    @classmethod
    def task_markup(cls, habit):
        plus_minus = '?-+±'[habit.down_available + habit.up_available * 2]
        return [('habit-plus_minus', plus_minus), ' '] + super().task_markup(habit)

    def __init__(self, habit):
        super().__init__(habit, text=self.task_markup(habit))
        self.habit = habit
        urwid.connect_signal(habit, 'update', self.on_update)

    def on_update(self):
        self.set_text(self.task_markup(self.habit))

    def keypress(self, size, key):
        if key in ACCEL_HABIT_PLUS:
            self.habit.score('up')
        elif key in ACCEL_HABIT_MINUS:
            self.habit.score('down')
        else:
            return super().keypress(size, key)


class CheckBoxBasedTaskWidget(TaskWidgetMixin, urwid.CheckBox):
    def __init__(self, task):
        super().__init__(task, label=self.task_markup(task), state=task.completed,
                         on_state_change=self.on_checkbox_toggle)
        urwid.connect_signal(task, 'update', self.on_model_update)

    @classmethod
    def value_attr(cls, task):
        if task.completed:
            return 'task-completed'
        return super().value_attr(task)

    def on_model_update(self):
        self.set_label(self.task_markup(self.task))
        self.set_state(self.task.completed)

    def on_checkbox_toggle(self, _, new_state):
        self.task.completed = new_state


class DailyWidget(CheckBoxBasedTaskWidget):
    @classmethod
    def task_markup(cls, daily):
        return [
            cls.value_markup(daily),
            ('daily-streak', '[{}] '.format(daily.streak)) if daily.streak else ' ',
            cls.text_markup(daily),
        ]

    def __init__(self, daily):
        super().__init__(daily)
        self.daily = daily


class TodoWidget(CheckBoxBasedTaskWidget):
    def __init__(self, todo):
        super().__init__(todo)
        self.todo = todo


class RewardWidget(TaskWidgetMixin, urwid.Button):
    @classmethod
    def value_markup(cls, reward):
        return 'gold', '({r.value})'.format(r=reward)

    def __init__(self, reward):
        super().__init__(reward, label=self.task_markup(reward))
        self.reward = reward
