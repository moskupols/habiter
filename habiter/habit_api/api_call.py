import requests
from habiter.habit_api.exceptions import HabitAPIUnavailableException, HabitAPIException


class Deferred:
    def __init__(self, action, errback=None, args=(), err_args=()):
        self.actions = [(action, args, errback, err_args, False)]

        self._done = False
        self.result = None
        self.exception = None

    def chain_action(self, action, errback=None, prev_result=True, args=(), err_args=())->'Deferred':
        self.actions.append((action, args, errback, err_args, prev_result))
        return self

    def __call__(self):
        assert not self.done
        for action, args, errback, err_args, prev_result in self.actions:
            if prev_result:
                args = (self.result,) + args
            try:
                self.result = action(*args)
            except Exception as e:
                self.exception = e
                if errback:
                    errback(*err_args)
                    return
                raise
        self._done = True
        return self.result

    @property
    def done(self):
        return self._done


class DeferredAPICall(Deferred):
    def __init__(self, description, request, session, timeout, postproc=None, **kwargs):
        self.description = description
        self.session = session
        self.request = request
        self.timeout = timeout
        self.postproc = postproc
        super().__init__(action=self.__action, **kwargs)

    def __action(self):
        prepared = self.session.prepare_request(self.request)
        response = self.session.send(prepared, timeout=self.timeout)

        if response.ok:
            response = response.json()
            if self.postproc:
                response = self.postproc(response)
            return response
        if response.status_code >= 500:
            raise HabitAPIUnavailableException(response.reason)
        json = response.json()  # yes it can raise too
        raise HabitAPIException(json['err'])

    def __str__(self):
        return self.description

    def __repr__(self):
        return 'DeferredAPICall<{r.method} {r.url} {desc}>'.format(r=self.request, desc=self.description)


class DeferredAPICallFactory:
    def __init__(self, session, api_base_url, timeout):
        self.session = session
        self.timeout = timeout
        self.api_base_url = api_base_url

    def request(self, description, method, path, body=None, params=None, headers=None, **kwargs):
        url = self.api_base_url + path
        request = requests.Request(method, url, json=body, params=params, headers=headers)
        return DeferredAPICall(description, request, self.session, self.timeout, **kwargs)
