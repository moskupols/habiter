__author__ = 'moskupols'

from . import habit_api
from .settings import user_id, api_key
from pprint import pprint

def run():
    api = habit_api.HabitAPI(user_id, api_key)

    pprint(api.user())
