import urwid


class StatusBar(urwid.Text):
    def __init__(self, markup='initial status'):
        super().__init__(markup, wrap=urwid.CLIP)
