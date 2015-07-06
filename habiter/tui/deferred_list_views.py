from habiter.tui.deferred_widgets import DueDeferredWidget, DoneDeferredWidget
from habiter.tui.list_views import AbstractListView


class DueDeferredListView(AbstractListView):
    list_title = 'Deferred API calls'
    widget_cls = DueDeferredWidget


class DoneDeferredListView(AbstractListView):
    list_title = 'API call log'
    widget_cls = DoneDeferredWidget
