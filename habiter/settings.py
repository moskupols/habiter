try:
    from .secret import user_id, api_key
except ImportError:
    raise ImportError('you should create secret.py and initialize user_id and api_key there ._.')

palette = (
    ('list_title', 'bold', ''),
)

ACCEL_QUIT = 'qQ'
ACCEL_TOGGLE_LIST_MODE = 'mM'
