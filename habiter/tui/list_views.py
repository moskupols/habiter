import itertools
import urwid
from habiter.models.list_model import FilterListProxyModel, MappingListProxyModel
from habiter.settings import ACCEL_NEXT_LIST_FILTER


class AbstractListView(urwid.WidgetWrap, urwid.WidgetDecoration):
    list_title = ''
    widget_cls = None

    def __init__(self, data_model):
        self.data_model = data_model
        self._wid_model = MappingListProxyModel(data_model, self.widget_cls, cls=urwid.SimpleListWalker)

        self._list_box = urwid.ListBox(self._wid_model.list)
        self._line_box = urwid.LineBox(self._list_box, title=self.title_markup())

        urwid.WidgetWrap.__init__(self, self._line_box)
        urwid.WidgetDecoration.__init__(self, self._list_box)

    def set_title(self, new_title):
        return self._line_box.set_title(new_title)

    def title_markup(self):
        return self.list_title


class AbstractFilterListView(AbstractListView):
    no_filter = (lambda wid: True, 'all')
    task_filters = (no_filter,)

    def __init__(self, data_model):
        self._filters_ring = itertools.cycle(self.task_filters)
        self.cur_filter = next(self._filters_ring)

        self.filter_model = FilterListProxyModel(data_model, self.cur_filter[0])

        super().__init__(self.filter_model)

    def switch_to_next_filter(self):
        self.cur_filter = next(self._filters_ring)
        self.set_title(self.title_markup())
        self.filter_model.set_filter(self.cur_filter[0])

    def title_markup(self):
        return '{} ({})'.format(self.list_title, self.cur_filter[1])

    def keypress(self, size, key):
        if key in ACCEL_NEXT_LIST_FILTER:
            self.switch_to_next_filter()
        else:
            return super().keypress(size, key)
