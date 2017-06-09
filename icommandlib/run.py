import queue
import pyte
import pyuv
from icommandlib import messages as message
import pty


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

        self.loop = pyuv.Loop.default_loop()

        self.tty = pyuv.TTY(self.loop, self.master_fd, True)
        self.tty.start_read(self.on_tty_read)

        self.process = pyuv.Process.spawn(
            self.loop,
            args=icommand._command.arguments,
            env=icommand._command.env,
            cwd=icommand._command.directory,
            exit_callback=self.on_exit,
            stdio=[
                pyuv.StdIO(
                    fd=self.slave_fd,
                    flags=pyuv.UV_INHERIT_FD,
                ),
                pyuv.StdIO(
                    fd=self.slave_fd,
                    flags=pyuv.UV_INHERIT_FD,
                ),
                pyuv.StdIO(
                    fd=self.slave_fd,
                    flags=pyuv.UV_INHERIT_FD,
                ),
            ]
        )

        self.response_queue.put(
            message.ProcessStartedMessage(message.RunningProcess(
                self.process.pid, self.master_fd
            ))
        )

        self.async = pyuv.Async(self.loop, self.on_thread_callback)
        self.response_queue.put(message.AsyncSendMethodMessage(self.async.send))

        self.timeout_handle = None
        self.reset_timeout()

        self.loop.run()

    def on_thread_callback(self, async_handle):
        self.check()

    def timeout_handler(self, timer_handle):
        self.close_handles()
        self.response_queue.put(message.TimeoutMessage(self.timeout))

    def on_exit(self, proc, exit_status, term_signal):
        self.check()
        self.response_queue.put(
            message.ExitMessage(message.FinishedProcess(exit_status, term_signal))
        )

    def on_tty_read(self, handle, data, error):
        if data is None:
            pass
        else:
            self.stream.feed(data.decode('utf8'))
            self.raw_byte_output = self.raw_byte_output + data
            self.check()

    def check(self):
        if self.task is None:
            try:
                self.task = self.request_queue.get(block=False)
            except queue.Empty:
                self.task = None

        if self.task is not None:
            if isinstance(self.task, message.Condition):
                iscreen = IScreen(self.screen, self.raw_byte_output)

                if self.task.value(iscreen):
                    self.reset_timeout()
                    self.response_queue.put(message.OutputMatched())
                    self.task = None
            if isinstance(self.task, message.TakeScreenshot):
                self.response_queue.put(message.Screenshot(
                    "\n".join(line for line in self.screen.display)
                ))
                self.task = None

    def reset_timeout(self):
        if self.timeout is not None:
            if self.timeout_handle is not None:
                self.timeout_handle.close()
                self.timeout_handle = None
            self.timeout_handle = pyuv.Timer(self.loop)
            self.timeout_handle.start(self.timeout_handler, self.timeout, 0)

    def close_handles(self):
        if self.timeout_handle is not None and not self.timeout_handle.closed:
            self.timeout_handle.close()
            self.timeout_handle = None
        if not self.tty.closed:
            self.tty.close()
            self.tty = None
