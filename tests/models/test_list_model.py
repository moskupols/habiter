from unittest import TestCase
from functools import wraps
from habiter.models.list_model import ListModel


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

    @_change_test
    def test_set_at(self, li):
        li[2] = 9

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
