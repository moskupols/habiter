import urwid
from habiter import habit_api, models
from habiter.settings import USER_ID, API_KEY, PALETTE, RESET_TERMINAL_PALETTE
from habiter.synchronizer import Synchronizer
from habiter.tui import MainFrame

__author__ = 'moskupols'

from . import habit_api, tui


def run():
    api = habit_api.AuthorizedHabitAPI(USER_ID, API_KEY)
    user = models.user.User(api, Synchronizer())

    # user = Mock()
    # user.name = 'mocked name'

    main = MainFrame(user)

    loop = urwid.MainLoop(main, palette=PALETTE, handle_mouse=False)
    if RESET_TERMINAL_PALETTE:
        loop.screen.reset_default_terminal_palette()

    loop.run()
