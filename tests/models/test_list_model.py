from unittest import TestCase
from functools import wraps
from habiter.models.list_model import ListModel, FilterListProxyModel


def _change_test(change):
    @wraps(change)
    def test(self):
        for li in (self.list, self.model):
            change(self, li)
        self.assertSequenceEqual(self.list, self.model)

    return test


class TestListModel(TestCase):
    def setUp(self):
        self.list = [3, 1, 4, 1, 5]
        self.model = ListModel(self.list[:])

    @_change_test
    def test_insert_at_begin(self, li):
        li.insert(0, 9)

    @_change_test
    def test_insert_at_middle(self, li):
        li.insert(2, 6)
        li.insert(2, 7)

    @_change_test
    def test_insert_at_end(self, li):
        li.insert(len(li), 9)
        li.insert(-1, 10)

    @_change_test
    def test_set_at(self, li):
        li[2] = 9
        li[-1] = 2

    @_change_test
    def test_set_extended_slice(self, li):
        li[1:5:3] = [8, 9]

    @_change_test
    def test_set_plain_slice_same_size(self, li):
        li[:3] = [7, 8, 9]

    @_change_test
    def test_set_plain_slice_shorter(self, li):
        li[:4] = [8, 9]

    @_change_test
    def test_set_plain_slice_longer(self, li):
        li[:4] = [7, 8, 9, 7, 8, 9, 9, 9]

    @_change_test
    def test_set_whole_slice(self, li):
        li[:] = [1, 2, 3]

    @_change_test
    def test_clear(self, li):
        li.clear()

    @_change_test
    def test_del_at(self, li):
        del li[1]
        del li[-2]

    @_change_test
    def test_del_plain_slice(self, li):
        del li[1:20]

    @_change_test
    def test_del_extended_slice(self, li):
        del li[1:5:3]

    def test_get_slice(self):
        self.assertSequenceEqual(self.list[1:4], self.model[1:4])


class TestFilterListProxyModel(TestCase):
    def setUp(self):
        self.inner_list = [3, 2, 4, 1, 5, 6, 2]
        self.inner_model = ListModel(self.inner_list)
        self.filter = lambda x: x % 2
        self.proxy = FilterListProxyModel(self.inner_model, filter_=self.filter)

    def expected_list(self):
        return [x for x in self.inner_model if self.filter(x)]

    def assertConsistency(self):
        self.assertSequenceEqual(self.expected_list(), self.proxy)

    def test_init_filter(self):
        self.assertConsistency()

    def test_set_filter(self):
        self.filter = lambda x: not (x % 2)
        self.proxy.set_filter(self.filter)
        self.assertConsistency()

    def test_del_not_touching(self):
        del self.inner_model[self.inner_list.index(2)]
        self.assertConsistency()

    def test_del_removing(self):
        del self.inner_model[self.inner_list.index(1)]
        self.assertConsistency()

    def test_set_not_touching(self):
        self.inner_model[self.inner_list.index(2)] = 4
        self.assertConsistency()

    def test_set_inserting(self):
        self.inner_model[self.inner_list.index(2)] = 3
        self.assertConsistency()

    def test_set_removing(self):
        self.inner_model[self.inner_list.index(1)] = 2
