class Subject:
    def __init__(self):
        self._observers = {}

    def notify(self, signal):
        try:
            for observer in self._observers[signal]:
                observer.receive(self, signal)
        except ValueError:
            pass
        except KeyError:
            pass

    def attach(self, observer, signal):
        if signal not in self._observers:
            self._observers[signal] = [observer]
        elif observer not in self._observers[signal]:
            self._observers[signal].append(observer)

    def detach(self, observer, signal):
        try:
            self._observers[signal].remove(observer)
        except ValueError:
            pass
