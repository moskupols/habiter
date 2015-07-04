"""
This is the file to store all user-definable magic constants.

Of course, all these values are supposed to be got from some
decent config file, something like ~/.habiter. Somewhen I'll
do that. Nevertheless, current file could be the source of
the default settings.
"""

try:
    from .secret import USER_ID, API_KEY
except ImportError:
    USER_ID = 'c31fdbc0-15c5-44a8-8ef9-c8c8842b0266'
    API_KEY = '085e09c3-9a28-4828-a9e5-8dfb953f2dea'

# these are used to define colors for task value half-intervals.
# each half-interval is left-inclusive, right-exclusive.
#
# actually task values are real numbers, and are rounded for
# showing in task list
VALUE_COLOR_BOUNDS = (
    -10, -5, -0.9, 1, 5, 10,
)

# see http://urwid.org/manual/displayattributes.html
# for info on palette syntax
PALETTE = (
    ('name', 'bold', ''),
    ('level', '', ''),
    ('hp', 'light red', ''),
    ('exp', 'yellow', ''),
    ('mp', 'dark cyan', ''),
    ('gold', 'yellow,bold', ''),
    ('info_bar', '', ''),

    ('task-value_-10', 'black', 'dark red'),
    ('task-value_-10_-5', 'white', 'dark red'),
    ('task-value_-5_-0.9', 'black', 'brown'),
    ('task-value_-0.9_1', '', ''),
    ('task-value_1_5', 'black', 'dark green'),
    ('task-value_5_10', 'white', 'dark cyan'),
    ('task-value_10', 'white', 'dark blue'),

    ('habit-plus_minus', 'bold', ''),
)

RESET_TERMINAL_PALETTE = False

ACCEL_QUIT = 'qQ'
ACCEL_TOGGLE_LIST_MODE = 'mM'
