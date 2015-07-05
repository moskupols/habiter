from collections import deque
from habiter.models.list_model import ListModel


class Synchronizer:
    def __init__(self):
        self.due_calls = ListModel(deque())
        self.done_calls = ListModel(deque())

    def add_call(self, call):
        if call.request.method.lower() == 'get':
            self.due_calls.append(call)
        else:
            self.done_calls.append(call)

    def perform_one_call(self):
        self.due_calls[0]()
        self.done_calls.append(self.due_calls.pop(0))
