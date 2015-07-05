import urwid
from habiter.utils import signalling


@signalling(['update_at', 'insert_at', 'remove_at', 'reset'])
class ListModel:
    def __init__(self, li: list=None):
        self.list = li or []

    def insert(self, at, value):
        self.list.insert(at, value)
        urwid.emit_signal(self, 'insert_at', at, value)

    def append(self, value):
        self.insert(len(self), value)

    def pop(self, at=-1):
        result = self.list.pop(at)
        urwid.emit_signal(self, 'remove_at', at, result)
        return result

    def clear(self):
        self.list.clear()
        urwid.emit_signal(self, 'reset')

    def __setitem__(self, key, value):
        self.list[key] = value
        urwid.emit_signal(self, 'update_at', key, value)

    def __getitem__(self, at):
        return self.list[at]

    def __delitem__(self, key):
        self.pop(key)

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return self.list.__iter__()

    def __reversed__(self):
        return self.list.__reversed__()

    def __contains__(self, item):
        return self.list.__contains__(item)


@signalling(ListModel.SIGNALS)
class MappingListModelProxy(ListModel):
    def __init__(self, model: ListModel, mapping, cls=list):
        self.source_model = model
        self.mapping = mapping
        super().__init__(cls(list(map(mapping, model))))

        urwid.connect_signal(model, 'update_at', self._on_setitem)
        urwid.connect_signal(model, 'remove_at', self._on_remove)
        urwid.connect_signal(model, 'insert_at', self._on_insert)
        urwid.connect_signal(model, 'reset', self._on_reset)

    def _on_remove(self, at, _):
        del self[at]

    def _on_setitem(self, at, value):
        super().__setitem__(at, self.mapping(value))

    def _on_insert(self, at, value):
        return super().insert(at, self.mapping(value))

    def _on_reset(self):
        self.list[:] = list(map(self.mapping, self.source_model))
