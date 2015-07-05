import urwid
from habiter.settings import VALUE_COLOR_BOUNDS, ACCEL_HABIT_PLUS, ACCEL_HABIT_MINUS


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
        return cls.value_attr(task), '[{}]'.format(round(task.value, 3))


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
        urwid.connect_signal(habit, 'update', self.on_update)

    def on_update(self):
        self.set_text(self.markup_for(self.habit))

    def keypress(self, size, key):
        if key in ACCEL_HABIT_PLUS:
            self.habit.score('up')
        elif key in ACCEL_HABIT_MINUS:
            self.habit.score('down')
        else:
            return super().keypress(size, key)


class CheckBoxBasedTaskWidget(TaskWidgetMixin, urwid.CheckBox):
    def __init__(self, task):
        super().__init__(task, label=self.label_for(task), state=task.completed,
                         on_state_change=self.on_checkbox_toggle)
        urwid.connect_signal(task, 'update', self.on_model_update)

    @classmethod
    def value_attr(cls, task):
        if task.completed:
            return 'task-completed'
        return super().value_attr(task)

    @classmethod
    def label_for(cls, task):
        raise NotImplementedError

    def on_model_update(self):
        self.set_label(self.label_for(self.task))
        self.set_state(self.task.completed)

    def on_checkbox_toggle(self, _, new_state):
        self.task.completed = new_state


class DailyWidget(CheckBoxBasedTaskWidget):
    @classmethod
    def label_for(cls, daily):
        return [
            cls.value_markup(daily),
            ('daily-streak', '[{}] '.format(daily.streak)) if daily.streak else ' ',
            ('task-text', daily.text),
        ]

    def __init__(self, daily):
        super().__init__(daily)
        self.daily = daily


class TodoWidget(CheckBoxBasedTaskWidget):
    @classmethod
    def label_for(cls, todo):
        return [
            cls.value_markup(todo), ' ',
            ('task-text', todo.text),
        ]

    def __init__(self, todo):
        super().__init__(todo)
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
