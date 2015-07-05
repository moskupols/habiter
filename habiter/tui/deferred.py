import urwid
from habiter.models.list_model import MappingListModelProxy


class DueDeferredWidget(urwid.WidgetWrap):
    def __init__(self, deferred):
        self.deferred = deferred
        super().__init__(urwid.Text(str(deferred)))


DoneDeferredWidget = DueDeferredWidget


class ListView(urwid.WidgetWrap):
    def __init__(self, list_model, mapping):
        self.list_model = list_model
        self.wid_model = MappingListModelProxy(list_model, mapping, cls=urwid.SimpleListWalker)
        super().__init__(urwid.ListBox(self.wid_model.list))
