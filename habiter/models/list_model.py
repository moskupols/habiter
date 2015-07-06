import itertools
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

    def __set_at(self, at, value):
        self.list[at] = value
        urwid.emit_signal(self, 'update_at', at, value)

    def __setitem__(self, key, value):
        # based on http://code.activestate.com/recipes/440656-list-mixin/
        if isinstance(key, slice):
            start, stop, stride = key.indices(len(self))
            indices = range(start, stop, stride)
            if stride != 1:
                assert len(indices) == len(value)
                for i, v in zip(indices, value):
                    self.__set_at(i, v)
            else:
                new_indices = range(start, start + len(value))
                for i, j, v in itertools.zip_longest(indices, new_indices, value):
                    if i is None:
                        self.insert(j, v)
                    elif j is None:
                        del self[i]
                    else:
                        assert i == j
                        self.__set_at(i, v)
        else:
            self.__set_at(key, value)

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
        if isinstance(at, slice):
            self[at] = [self.mapping(v) for v in value]
        else:
            self[at] = self.mapping(value)

    def _on_insert(self, at, value):
        return self.insert(at, self.mapping(value))
