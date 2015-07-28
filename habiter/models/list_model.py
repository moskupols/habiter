from bisect import bisect, bisect_left
import itertools
import urwid
from habiter.utils import signalling
from collections.abc import MutableSequence, Callable


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
            if stride != 1:  # extended slice
                assert len(indices) == len(value)
                for i, v in zip(indices, value):
                    self.__set_at(i, v)
            else:
                new_indices = range(start, start + len(value))
                for i, j, v in itertools.zip_longest(indices, new_indices, value):
                    if i is not None and j is not None:
                        assert i == j
                        self.__set_at(i, v)
                    elif i is None:  # more new values than old
                        self.insert(j, v)
                    else:  # more old values than new, delete the remaining segment right:
                        assert i is not None
                        del self[i:stop]
                        break
        else:
            self.__set_at(key, value)

    def __del_at(self, at):
        del self.list[at]
        urwid.emit_signal(self, 'remove_at', at)

    def __delitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            indices = range(start, stop, step)
            if step > 0:
                indices = reversed(indices)
            for i in indices:
                self.__del_at(i)
        else:
            self.__del_at(key)

    def __len__(self):
        return len(self.list)

    def __str__(self):
        return self.__class__.__name__ + ' on ' + str(self.list)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.list) + ')'


class AbstractModelWatcher:
    def __init__(self, watched_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watched_model = watched_model

        urwid.connect_signal(watched_model, 'update_at', self._on_setitem)
        urwid.connect_signal(watched_model, 'remove_at', self._on_remove)
        urwid.connect_signal(watched_model, 'insert_at', self._on_insert)

    def _on_remove(self, at):
        raise NotImplementedError

    def _on_setitem(self, at, value):
        raise NotImplementedError

    def _on_insert(self, at, value):
        raise NotImplementedError


@signalling(ListModel.SIGNALS)
class MappingListProxyModel(AbstractModelWatcher, ListModel):
    def __init__(self, model: ListModel, mapping, cls=list):
        self.mapping = mapping
        super().__init__(model, cls(list(map(mapping, model))))

    def _on_remove(self, at):
        del self[at]

    def _on_setitem(self, at, value):
        self[at] = self.mapping(value)

    def _on_insert(self, at, value):
        return self.insert(at, self.mapping(value))


@signalling(ListModel.SIGNALS)
class FilterListProxyModel(AbstractModelWatcher, ListModel):  # hi qt
    def __init__(self, model: ListModel, filter_: Callable, cls=list):
        self.source_model = model
        super().__init__(model, cls(model))

        self.filter = filter_
        self.subseq = list(range(len(model)))
        self.set_filter(filter_)

    def set_filter(self, new_filter):
        self.filter = new_filter
        sub_enum = [(i, v) for i, v in enumerate(self.source_model) if new_filter(v)]
        self.subseq, new_list = map(list, zip(*sub_enum)) if len(sub_enum) else ([], [])
        self[:] = new_list

    def _on_insert(self, at, value):
        if not self.filter(value):
            return
        sub_index = bisect(self.subseq, at)
        self.subseq.insert(sub_index, at)
        self.insert(sub_index, value)

    def _on_setitem(self, at, value):
        sub_index = bisect_left(self.subseq, at)
        if sub_index != len(self.subseq):
            self[sub_index] = value

    def _on_remove(self, at):
        sub_index = bisect_left(self.subseq, at)
        if sub_index != len(self.subseq):
            del self.subseq[sub_index]
            del self[sub_index]
