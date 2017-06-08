import commandlib
import pyte
import subprocess
import os
import pty
import psutil
import pyuv
import time
from copy import copy
from icommandlib import exceptions
import threading
import queue


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


class Condition(Message):
    pass


class OutputMatched(Message):
    def __init__(self):
        self._value = None


class TimeoutMessage(Message):
    pass


class TakeScreenshot(Message):
    def __init__(self):
        self._value = None


class Screenshot(Message):
    pass


class IProcess(object):
    def __init__(self, icommand):
        self._icommand = icommand
        self._request_queue = queue.Queue()
        self._response_queue = queue.Queue()
        self._handle = threading.Thread(
            target=IProcessHandle,
            args=(icommand, self._request_queue, self._response_queue)
        )
        self._handle.start()
        self._pid = self._expect_message(PIDMessage)
        self._master = self._expect_message(FDMessage)
        self._async_send = self._expect_message(AsyncSendMethodMessage)

    def _expect_message(self, of_kind):
        response = self._response_queue.get()
        if isinstance(response, TimeoutMessage):
            raise exceptions.IProcessTimeout(
                "Timed out after {0} seconds.".format(response.value)
            )
        if not isinstance(response, of_kind):
            raise Exception(
                "Threading error expected {0} got {1}".format(
                    type(of_kind), type(of_kind)
                )
            )
        return response.value

    def wait_until_output_contains(self, text):
        self._request_queue.put(Condition(
            lambda iscreen: text in iscreen.raw_bytes.decode('utf8')
        ))
        self._async_send()
        self._expect_message(OutputMatched)

    def wait_until_on_screen(self, text):
        self._request_queue.put(Condition(
            lambda iscreen: len([line for line in iscreen.display if text in line]) > 0
        ))
        self._async_send()
        self._expect_message(OutputMatched)

    def send_keys(self, text):
        os.write(self._master, text.encode('utf8'))

    def screenshot(self):
        self._request_queue.put(TakeScreenshot())
        self._async_send()
        return self._expect_message(Screenshot)

    def wait_for_finish(self):
        psutil.Process(self._pid).wait()


class IScreen(object):
    """
    Represents the output of a process, either as raw bytes
    or on a virtual terminal.
    """
    def __init__(self, screen, raw_byte_output):
        self.screen = screen
        self.raw_bytes = raw_byte_output

    @property
    def display(self):
        return self.screen.display


class IProcessHandle(object):
    def __init__(self, icommand, request_queue, response_queue):
        self._request_queue = request_queue
        self._response_queue = response_queue
        self._icommand = icommand
        self._master, self._slave = pty.openpty()
        self._stream = pyte.Stream()
        self._screen = pyte.Screen(80, 24)
        self._stream.attach(self._screen)
        self._timeout_triggered = False
        self._raw_byte_output = b''
        self._closing = False
        self._timeout = icommand._timeout
        self._task = None
        self._start_time = time.time()
        self._process = subprocess.Popen(
            icommand._command.arguments,
            bufsize=0,  # Ensures that all stdout/err is pushed to us immediately.
            stdout=self._slave,
            stderr=self._slave,
            stdin=self._slave,
            env=icommand._command.env,
        )
        self._response_queue.put(PIDMessage(self.pid))
        self._response_queue.put(FDMessage(self._master))

        self.loop = pyuv.Loop.default_loop()

        self.async = pyuv.Async(self.loop, self._on_thread_callback)
        self._response_queue.put(AsyncSendMethodMessage(self.async.send))

        self.tty = pyuv.TTY(self.loop, self._master, True)
        self.tty.start_read(self._on_tty_read)

        self.timer_handler = None
        self._reset_timeout()

        self.loop.run()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        assert type(value) is float, "timeout value must be a float"
        self._timeout = value

    @property
    def pid(self):
        return self._process.pid

    @property
    def psutil(self):
        return psutil.Process(self.pid)

    def _on_thread_callback(self, async_handle):
        self._check()

    def _timeout_handler(self, timer_handle):
        self._close_handles()
        self._response_queue.put(TimeoutMessage(self._timeout))

    def _on_tty_read(self, handle, data, error):
        if data is None:
            pass
        else:
            self._stream.feed(data.decode('utf8'))
            self._raw_byte_output = self._raw_byte_output + data
            self._check()

    def _check(self):
        if self._task is None:
            try:
                self._task = self._request_queue.get(block=False)
            except queue.Empty:
                self._task = None

        if self._task is not None:
            if isinstance(self._task, Condition):
                iscreen = IScreen(self._screen, self._raw_byte_output)

                if self._task.value(iscreen):
                    self._reset_timeout()
                    self._response_queue.put(OutputMatched())
                    self._task = None
            if isinstance(self._task, TakeScreenshot):
                self._response_queue.put(Screenshot(
                    "\n".join(line for line in self._screen.display)
                ))
                self._task = None

    def _reset_timeout(self):
        if self._timeout is not None:
            if self.timer_handler is not None:
                self.timer_handler.close()
                self.timer_handler = None
            self.timer_handler = pyuv.Timer(self.loop)
            self.timer_handler.start(self._timeout_handler, self._timeout, 0)

    def _close_handles(self):
        self._closing = True
        if self.timer_handler is not None and not self.timer_handler.closed:
            self.timer_handler.close()
            self.timer_handler = None
        if not self.tty.closed:
            self.tty.close()
            self.tty = None


class ICommand(object):
    def __init__(self, command):
        assert isinstance(command, commandlib.Command), "must be type 'commandlib.Command'"
        self._command = command
        self._timeout = None

    def with_timeout(self, value):
        assert type(value) is float, "timeout value must be a float"
        new_icommand = copy(self)
        new_icommand._timeout = value
        return new_icommand

    def run(self):
        return IProcess(self)
