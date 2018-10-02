from icommandlib import messages as message
import signal
import psutil
import queue
import pyte
import pyuv
import pty
import os


class IScreen(object):
    """
    Represents the output of a process, both as raw bytes
    and a virtual terminal (screen).
    """
    def __init__(self, screen, raw_byte_output):
        self.screen = screen
        self.raw_bytes = raw_byte_output

    @property
    def display(self):
        return self.screen.display

    @property
    def text(self):
        return u'\n'.join(self.display)


class IProcessHandle(object):
    """
    Starts and then manages with the process directly.

    The IProcessHandle operates in its own thread which operates and
    reports to the main thread in response to the following events:

    * The process exiting of its own accord.
    * Orders from the master thread.
    * A timer (used for timing out waits).
    * Chunks of output spat out at the terminal (fed into virtual terminal).
    """
    def __init__(self, icommand, order_queue, event_queue):
        try:
            self.order_queue = order_queue   # Messages from master thread
            self.event_queue = event_queue   # Messages to master thread

            self.master_fd, self.slave_fd = pty.openpty()

            self.stream = pyte.Stream()
            self.screen = pyte.Screen(icommand.width, icommand.height)
            self.stream.attach(self.screen)
            self.raw_byte_output = b''
            self.timeout = icommand.timeout
            self.task = None

            self.loop = pyuv.Loop.default_loop()

            self.tty_handle = pyuv.TTY(self.loop, self.master_fd, True)
            self.tty_handle.start_read(self.on_tty_read)

            self.sigterm_handle = pyuv.Signal(self.loop)
            self.sigterm_handle.start(self.sigterm_callback, signal.SIGTERM)
            self.sigint_handle = pyuv.Signal(self.loop)
            self.sigint_handle.start(self.sigint_callback, signal.SIGINT)

            self.process_handle = pyuv.Process.spawn(
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
                ],
                flags=pyuv.UV_PROCESS_DETACHED,
            )

            self._pid = self.process_handle.pid

            self.event_queue.put(
                message.ProcessStartedMessage(message.RunningProcess(
                    self._pid, self.master_fd
                ))
            )

            self.async_handle = pyuv.Async(self.loop, self.on_thread_callback)
            self.event_queue.put(message.AsyncSendMethodMessage(self.async_handle.send))

            self.timeout_handle = None
            self.reset_timeout()

            self.loop.run()
        except Exception as error:
            self.close_handles()
            self.event_queue.put(message.ExceptionMessage(error))

    def screenshot(self):
        """
        Get a current screenshot of the screen as a string.
        """
        return u"\n".join(line for line in self.screen.display)

    @property
    def psutil(self):
        return psutil.Process(self._pid)

    def on_thread_callback(self, async_handle):
        """
        This is the callback that is triggered when self.async.send()
        (the only threadsafe method on this class) is called.

        It is used to indicate that there's a message waiting on
        self._order_queue to pick up.
        """
        self.check_order_queue()

    def signal_callback(self, handle, signum):
        """
        Callback that is triggered by the parent process receiving
        a sigterm or sigint.
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            proc = psutil.Process(self.process_handle.pid)
            for descendant in proc.children(recursive=True):
                descendant.kill()
            proc.kill()
        self.check_order_queue()
        self.close_handles()
        self.event_queue.put(
            message.ExitMessage(message.FinishedProcess(
                None,
                9,
                '\n'.join(self.screen.display),
            ))
        )

    def sigterm_callback(self, handle, signum):
        self.signal_callback(handle, signum)

    def sigint_callback(self, handle, signum):
        self.signal_callback(handle, signum)

    def timeout_handler(self, timer_handle):
        """
        Callback that is triggered by the timer indicating a timeout.

        The timer is reset every time a condition is met.
        """
        self.close_handles()
        self.event_queue.put(
            message.TimeoutMessage(self.timeout, self.screenshot())
        )

    def on_exit(self, proc, exit_status, term_signal):
        """
        Callback that is triggered when the process exits of its
        own accord. Takes a screenshot and tells the control thread
        that we're done.
        """
        self.check_order_queue()
        self.close_handles()
        self.event_queue.put(
            message.ExitMessage(message.FinishedProcess(
                exit_status,
                term_signal,
                '\n'.join(self.screen.display),
            ))
        )

    def on_tty_read(self, handle, data, error):
        """
        Callback that is triggered when the process spews a chunk
        of data.
        """
        if data is None:
            pass
        else:
            self.stream.feed(data.decode('utf8'))
            self.raw_byte_output = self.raw_byte_output + data
            self.check_order_queue()

    def check_order_queue(self):
        """
        Callback that is triggered when there is (probably) a message
        waiting on the order queue.
        """
        try:
            if self.task is None:
                try:
                    self.task = self.order_queue.get(block=False)
                except queue.Empty:
                    self.task = None

            if self.task is not None:
                if isinstance(self.task, message.KillProcess):
                    for descendant in self.psutil.children(recursive=True):
                        descendant.kill()
                    self.psutil.kill()
                    self.close_handles()
                    self.event_queue.put(message.ProcessKilled())
                if isinstance(self.task, message.KeyPresses):
                    os.write(self.master_fd, self.task.value)
                    self.task = None
                elif isinstance(self.task, message.Condition):
                    self.reset_timeout(self.task.timeout)
                    iscreen = IScreen(self.screen, self.raw_byte_output)

                    if self.task.condition_function(iscreen):
                        self.event_queue.put(message.OutputMatched())
                        self.task = None
                elif isinstance(self.task, message.TakeScreenshot):
                    self.event_queue.put(message.Screenshot(
                        self.screenshot()
                    ))
                    self.task = None

        except Exception as error:
            self.close_handles()
            self.event_queue.put(message.ExceptionMessage(error))

    def reset_timeout(self, timeout=None):
        """
        Clears the timeout handle if it's there and sets a new one
        if timeout is set.
        """
        self.timeout = None
        if self.timeout_handle is not None:
            self.timeout_handle.close()
            self.timeout_handle = None
        if timeout is not None:
            self.timeout = timeout
            self.timeout_handle = pyuv.Timer(self.loop)
            self.timeout_handle.start(self.timeout_handler, timeout, 0)

    def close_handles(self):
        """
        Shut down all the callbacks.
        """
        if self.timeout_handle is not None and not self.timeout_handle.closed:
            self.timeout_handle.close()
            self.timeout_handle = None
        if not self.tty_handle.closed:
            self.tty_handle.close()
            self.tty_handle = None
        if not self.async_handle.closed:
            self.async_handle.close()
            self.async_handle = None
        if not self.process_handle.closed:
            self.process_handle.close()
            self.process_handle = None
        if not self.sigint_handle.closed:
            self.sigint_handle.close()
            self.sigint_handle = None
        if not self.sigterm_handle.closed:
            self.sigterm_handle.close()
            self.sigterm_handle = None
