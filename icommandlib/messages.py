

class Message(object):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class PIDMessage(Message):
    pass


class FDMessage(Message):
    pass


class AsyncSendMethodMessage(Message):
    pass


class RunningProcess(object):
    def __init__(self, pid, stdin):
        self._pid = pid
        self._stdin = stdin


class FinishedProcess(object):
    def __init__(self, exit_code, term_signal, screenshot):
        self.exit_code = exit_code
        self.term_signal = term_signal
        self.screenshot = screenshot


class ExitMessage(Message):
    pass


class ExceptionMessage(Message):
    pass


class ProcessStartedMessage(Message):
    pass


class Condition(Message):
    pass


class OutputMatched(Message):
    def __init__(self):
        self._value = None


class TimeoutMessage(Message):
    pass


class KeyPresses(Message):
    pass


class TakeScreenshot(Message):
    def __init__(self):
        self._value = None


class Screenshot(Message):
    pass
