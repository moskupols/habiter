import urwid
from habiter.utils import signalling
from collections.abc import MutableSequence


@signalling(['update_at', 'insert_at', 'remove_at'])
class ListModel(MutableSequence):
    def __init__(self, li: list=None):
        self.list = li or []

    def insert(self, at, value):
        self.list.insert(at, value)
        urwid.emit_signal(self, 'insert_at', at, value)

    def clear(self):
        del self[:]

    def __getitem__(self, at):
        return self.list[at]

    def __setitem__(self, key, value):
        self.list[key] = value
        if self.list[key] != value:
            urwid.emit_signal(self, 'update_at', key, value)

    def __delitem__(self, key):
        del self.list[key]
        urwid.emit_signal(self, 'remove_at', key)

    def __len__(self):
        return len(self.list)


@signalling(ListModel.SIGNALS)
class MappingListModelProxy(ListModel):
    def __init__(self, model: ListModel, mapping, cls=list):
        self.source_model = model
        self.mapping = mapping
        super().__init__(cls(list(map(mapping, model))))

        urwid.connect_signal(model, 'update_at', self._on_setitem)
        urwid.connect_signal(model, 'remove_at', self._on_remove)
        urwid.connect_signal(model, 'insert_at', self._on_insert)

    def _on_remove(self, at):
        del self[at]

    def _on_setitem(self, at, value):
        self[at] = self.mapping(value)

    def _on_insert(self, at, value):
        return self.insert(at, self.mapping(value))
