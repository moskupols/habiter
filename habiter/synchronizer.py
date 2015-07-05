
class Synchronizer:
    def add_call(self, call):
        if call.request.method.lower() == 'get':
            call()
