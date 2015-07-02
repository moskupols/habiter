try:
    from .secret import user_id, api_key
except ImportError:
    user_id = 'c31fdbc0-15c5-44a8-8ef9-c8c8842b0266'
    api_key = '085e09c3-9a28-4828-a9e5-8dfb953f2dea'

palette = (
    ('name', 'bold', ''),
    ('level', '', ''),
    ('hp', 'light red', ''),
    ('exp', 'yellow', ''),
    ('mp', 'dark cyan', ''),
    ('gold', 'yellow,bold', ''),
    ('info_bar', '', ''),
)

ACCEL_QUIT = 'qQ'
ACCEL_TOGGLE_LIST_MODE = 'mM'
