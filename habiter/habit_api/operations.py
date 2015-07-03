import requests
from habiter.habit_api.exceptions import HabitAPIUnavailableException, HabitAPIException


class DelayedOperation:
    def __init__(self, callback=None):
        self.callback = callback
        self._done = False
        self.result = None

    def __call__(self):
        assert not self._done
        self.result = self.action()
        self._done = True
        if self.callback:
            self.callback(self.result, self)
        return self.result

    def action(self):
        raise NotImplementedError

    @property
    def done(self):
        return self._done


class DelayedAPICall(DelayedOperation):
    def __init__(self, request, session, description, timeout=None, postproc=None, **kwargs):
        super().__init__(**kwargs)
        self.description = description
        self.session = session
        self.request = request
        self.timeout = timeout
        self.postproc = postproc

    def action(self):
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
        return 'RequestOperation({r.method} {r.url} {desc})'.format(r=self.request, desc=self.description)


class DelayedAPICallFactory:
    def __init__(self, session, api_base_url, timeout=None):
        self.session = session
        self.timeout = timeout
        self.api_base_url = api_base_url

    def request(self, description, method, path, body=None, params=None, headers=None, **kwargs):
        url = self.api_base_url + path
        request = requests.Request(method, url, json=body, params=params, headers=headers)
        return DelayedAPICall(request, self.session, description, timeout=self.timeout, **kwargs)
