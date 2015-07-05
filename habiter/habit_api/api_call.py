import requests
from habiter.habit_api.exceptions import HabitAPIUnavailableException, HabitAPIException


class Deferred:
    def __init__(self, action, errback=None, args=(), err_args=()):
        self.action = action
        self.args = args

        self.errback = errback
        self.err_args = err_args

        self._done = False
        self.result = None
        self.exception = None

    def __call__(self):
        assert not self.done
        try:
            self.result = self.action(*self.args)
            self._done = True
            return self.result
        except Exception as e:
            self.exception = e
            if self.errback:
                self.errback(self, *self.err_args)
                return
            raise

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
