import queue
import pyte
import subprocess
import pyuv
from icommandlib import messages as message
import pty
import time


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
    """
    Starts and then manages with the process directly.

    The IProcessHandle operates in its own thread which operates upon
    the following events:

    * The process ending of its own accord.
    * The process spitting out a chunk of output (which is fed into
    a virtual terminal).
    * A timer (used for timing out other events).
    * Messages from the process thread.
    """
    def __init__(self, icommand, request_queue, response_queue):
        self.request_queue = request_queue       # Messages from master thread
        self.response_queue = response_queue     # Messages to master thread

        self.master_fd, self.slave_fd = pty.openpty()
        self.stream = pyte.Stream()
        self.screen = pyte.Screen(80, 24)
        self.stream.attach(self.screen)
        self.raw_byte_output = b''
        self.timeout = icommand.timeout
        self.task = None

        self.process = subprocess.Popen(
            icommand._command.arguments,
            bufsize=0,  # Ensures that all stdout/err is pushed to us immediately.
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            stdin=self.slave_fd,
            env=icommand._command.env,
        )

        self.response_queue.put(
            message.ProcessStartedMessage(message.RunningProcess(
                self.process.pid, self.master_fd
            ))
        )

        self.loop = pyuv.Loop.default_loop()

        self.async = pyuv.Async(self.loop, self._on_thread_callback)
        self.response_queue.put(message.AsyncSendMethodMessage(self.async.send))

        self.tty = pyuv.TTY(self.loop, self.master_fd, True)
        self.tty.start_read(self._on_tty_read)

        self.timeout_handle = None
        self._reset_timeout()

        self.loop.run()

    def _on_thread_callback(self, async_handle):
        self._check()

    def _timeout_handler(self, timer_handle):
        self._close_handles()
        self.response_queue.put(message.TimeoutMessage(self.timeout))

    def _on_tty_read(self, handle, data, error):
        if data is None:
            pass
        else:
            self.stream.feed(data.decode('utf8'))
            self.raw_byte_output = self.raw_byte_output + data
            self._check()

    def _check(self):
        if self.task is None:
            try:
                self.task = self.request_queue.get(block=False)
            except queue.Empty:
                self.task = None

        if self.task is not None:
            if isinstance(self.task, message.Condition):
                iscreen = IScreen(self.screen, self.raw_byte_output)

                if self.task.value(iscreen):
                    self._reset_timeout()
                    self.response_queue.put(message.OutputMatched())
                    self.task = None
            if isinstance(self.task, message.TakeScreenshot):
                self.response_queue.put(message.Screenshot(
                    "\n".join(line for line in self.screen.display)
                ))
                self.task = None

    def _reset_timeout(self):
        if self.timeout is not None:
            if self.timeout_handle is not None:
                self.timeout_handle.close()
                self.timeout_handle = None
            self.timeout_handle = pyuv.Timer(self.loop)
            self.timeout_handle.start(self._timeout_handler, self.timeout, 0)

    def _close_handles(self):
        if self.timeout_handle is not None and not self.timeout_handle.closed:
            self.timeout_handle.close()
            self.timeout_handle = None
        if not self.tty.closed:
            self.tty.close()
            self.tty = None
