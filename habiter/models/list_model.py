import urwid
from habiter.utils import signalling


@signalling(['update_at', 'insert_at', 'remove_at', 'reset'])
class ListModel:
    def __init__(self, li: list=None):
        self._list = li or []

    def insert(self, at, value):
        self._list.insert(at, value)
        urwid.emit_signal(self, 'insert_at', at, value)

    def append(self, value):
        self.insert(len(self), value)

    def pop(self, at=-1):
        result = self._list.pop(at)
        urwid.emit_signal(self, 'remove_at', at, result)
        return result

    def clear(self):
        self._list.clear()
        urwid.emit_signal(self, 'reset')

    def __setitem__(self, key, value):
        self._list[key] = value
        urwid.emit_signal(self, 'update_at', key, value)

    def __getitem__(self, at):
        return self._list[at]

    def __delitem__(self, key):
        self.pop(key)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return self._list.__iter__()

    def __reversed__(self):
        return self._list.__reversed__()

    def __contains__(self, item):
        return self._list.__contains__(item)


class MappingListModelProxy(ListModel):
    def __init__(self, model: ListModel, mapping, cls=list):
        self.model = model
        self.mapping = mapping
        super().__init__(cls(map(mapping, model)))

    def __setitem__(self, key, value):
        return super().__setitem__(key, self.mapping(value))

    def insert(self, at, value):
        return super().insert(at, self.mapping(value))
