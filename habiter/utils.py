import urwid

def signalling(signals):
    def _signalling(cls):
        urwid.register_signal(cls, signals)
        return cls
    return _signalling
