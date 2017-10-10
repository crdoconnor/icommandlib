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
        return '\n'.join(self.display)


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
        try:
            self.request_queue = request_queue       # Messages from master thread
            self.response_queue = response_queue     # Messages to master thread

            self.master_fd, self.slave_fd = pty.openpty()
            self.stream = pyte.Stream()
            self.screen = pyte.Screen(icommand.width, icommand.height)
            self.stream.attach(self.screen)
            self.raw_byte_output = b''
            self.timeout = icommand.timeout
            self.task = None

            self.loop = pyuv.Loop.default_loop()

            self.tty = pyuv.TTY(self.loop, self.master_fd, True)
            self.tty.start_read(self.on_tty_read)
            
            self.sigterm_handle = pyuv.Signal(self.loop)
            self.sigterm_handle.start(self.sigterm_callback, signal.SIGTERM)
            self.sigint_handle = pyuv.Signal(self.loop)
            self.sigint_handle.start(self.sigint_callback, signal.SIGINT)

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
                ],
                flags=pyuv.UV_PROCESS_DETACHED,
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
        except Exception as error:
            self.close_handles()
            self.response_queue.put(message.ExceptionMessage(error))

    def on_thread_callback(self, async_handle):
        """
        This is the callback that is triggered when self.async.send()
        (the only threadsafe method on this class) is called from
        IProcess to indicate a message waiting on the request queue.
        """
        self.check()
    
    def signal_callback(self, handle, signum):
        """
        Callback that is triggered by the parent process receiving
        a sigterm or sigint.
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            proc = psutil.Process(self.process.pid)
            for descendant in proc.children(recursive=True):
                  descendant.kill()
            proc.kill()
        self.check()
        self.close_handles()
        self.response_queue.put(
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
        self.response_queue.put(message.TimeoutMessage(self.timeout))

    def on_exit(self, proc, exit_status, term_signal):
        """
        Callback that is triggered when the process exits of its
        own accord. Takes a screenshot and tells the control thread
        that we're done.
        """
        self.check()
        self.close_handles()
        self.response_queue.put(
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
            self.check()

    def check(self):
        """
        Callback that is triggered when there is (probably) a message
        waiting on the request queue.
        """
        try:
            if self.task is None:
                try:
                    self.task = self.request_queue.get(block=False)
                except queue.Empty:
                    self.task = None

            if self.task is not None:
                if isinstance(self.task, message.KeyPresses):
                    os.write(self.master_fd, self.task.value)
                    self.task = None
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
        except Exception as error:
            self.close_handles()
            self.response_queue.put(message.ExceptionMessage(error))

    def reset_timeout(self):
        """
        Clears the timeout handle and sets a new one.
        """
        if self.timeout is not None:
            if self.timeout_handle is not None:
                self.timeout_handle.close()
                self.timeout_handle = None
            self.timeout_handle = pyuv.Timer(self.loop)
            self.timeout_handle.start(self.timeout_handler, self.timeout, 0)

    def close_handles(self):
        """
        Shut down all the callbacks.
        """
        if self.timeout_handle is not None and not self.timeout_handle.closed:
            self.timeout_handle.close()
            self.timeout_handle = None
        if not self.tty.closed:
            self.tty.close()
            self.tty = None
        if not self.async.closed:
            self.async.close()
            self.async = None
        if not self.process.closed:
            self.process.close()
            self.process = None
        if not self.sigint_handle.closed:
            self.sigint_handle.close()
            self.sigint_handle = None
        if not self.sigterm_handle.closed:
            self.sigterm_handle.close()
            self.sigterm_handle = None
