__author__ = 'moskupols'

from . import habit_api, models
from .settings import user_id, api_key
from pprint import pprint

def run():
    api = habit_api.HabitAPI(user_id, api_key)
    user = models.User(api)

    pprint(user.name)
    pprint(user.habits[0].data)
