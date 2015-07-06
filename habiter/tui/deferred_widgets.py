import urwid


class DueDeferredWidget(urwid.WidgetWrap):
    def __init__(self, deferred):
        self.deferred = deferred
        super().__init__(urwid.Text(str(deferred)))


DoneDeferredWidget = DueDeferredWidget

