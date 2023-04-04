from icommandlib import exceptions
from ptyprocess import PtyProcessUnicode
from icommandlib.utils import stripshot
import psutil
import signal
import select
import pyte
import time


class IScreen(object):
    """
    Represents the output of a process, both as raw bytes
    and a virtual terminal (screen).
    """

    def __init__(self, screen, raw_byte_output, stream):
        self.screen = screen
        self.raw_bytes = raw_byte_output
        self.stream = stream

    def feed(self, string):
        self.stream.feed(string)
        self.raw_bytes += string

    @property
    def display(self):
        return self.screen.display

    @property
    def text(self):
        return "\n".join(self.display)


class IProcess(object):
    """
    An interactive process.

        Start process by initializing with an commandlib.Command object.
    """

    def __init__(self, icommand):
        self._icommand = icommand
        # self._order_queue = queue.Queue()
        # self._event_queue = queue.Queue()
        # self._handle = threading.Thread(
        # target=IProcessHandle,
        # args=(icommand, self._order_queue, self._event_queue)
        # )
        # self._handle.start()

        # self._running_process = self._wait_for_event(message.ProcessStartedMessage)

        # self._pid = self._running_process._pid
        # self._master_fd = self._running_process._stdin
        # self._async_send = self._wait_for_event(message.AsyncSendMethodMessage)

        self._ptyprocess = PtyProcessUnicode.spawn(
            argv=icommand._command.arguments,
            env=icommand._command.env,
            cwd=icommand._command.directory,
            dimensions=(icommand.width, icommand.height),
        )
        self.psutil = psutil.Process(self._ptyprocess.pid)

        signal.signal(signal.SIGINT, self._die_gracefully)
        signal.signal(signal.SIGTERM, self._die_gracefully)

        self.stream = pyte.Stream()
        self.screen = pyte.Screen(icommand.width, icommand.height)
        self.stream.attach(self.screen)
        self.raw_byte_output = ""
        self.iscreen = IScreen(self.screen, self.raw_byte_output, self.stream)

        self._screenshot = ""
        self._final_screenshot = None
        self._running = True
        self._exit_code = None
        self.finished = False

    def _die_gracefully(self, *args):
        proc = psutil.Process(self.pid)
        for descendant in proc.children(recursive=True):
            descendant.kill()
        self._read()
        proc.kill()

    # def _check_events(self, expected=None):
    # try:
    # response = self._event_queue.get(block=False)
    # except queue.Empty:
    # response = None

    # if response is not None:
    # return self._handle_event(response, of_kind=expected)

    # def _handle_event(self, response, of_kind=None):
    # if isinstance(response, message.ExceptionMessage):
    # raise response.value
    # if isinstance(response, message.TimeoutMessage):
    # raise exceptions.IProcessTimeout(
    # "Timed out after {0} seconds:\n\n{1}".format(
    # response.after,
    # stripshot(response.screenshot),
    # )
    # )
    # if isinstance(response, message.ExitMessage):
    # self._running = False
    # self._pid = None
    # self._exit_code = response.value.exit_code
    # self._final_screenshot = response.value.screenshot
    # if of_kind != message.ExitMessage:
    # raise exceptions.UnexpectedExit(
    # response.value.exit_code,
    # response.value.screenshot,
    # )
    # if not isinstance(response, of_kind):
    # raise Exception(
    # "Threading error expected {0} got {1}".format(
    # type(of_kind), type(of_kind)
    # )
    # )
    # return response.value

    # def _wait_for_event(self, of_kind, timeout=None):
    # try:
    # response = self._event_queue.get(timeout=timeout)
    # except queue.Empty:
    # raise exceptions.IProcessTimeout(
    # "Timed out waiting for exit."
    # )
    # return self._handle_event(response, of_kind=of_kind)

    @property
    def pid(self):
        if not self.running:
            return None
        return self._ptyprocess.pid

    @property
    def running(self):
        if self.finished:
            return False
        try:
            if self.psutil.status() == "zombie":
                self._ptyprocess.wait()
                return False
        except psutil.NoSuchProcess:
            return False
        return self.psutil.is_running()

    @property
    def exit_code(self):
        # self._check_events(expected=message.ExitMessage)
        if self.running:
            return None
        try:
            if self.psutil.status() == "zombie":
                self._ptyprocess.wait()
                return self._ptyprocess.exitstatus
        except psutil.NoSuchProcess:
            pass
        if self._ptyprocess.exitstatus is None:
            import web_pdb

            web_pdb.set_trace()
        return self._ptyprocess.exitstatus

    def _read(self):
        fd = self._ptyprocess.fd

        if fd != -1:
            readable, _, _ = select.select([fd], [], [], 0.01)

            if len(readable) == 0:
                time.sleep(0.01)
            else:
                try:
                    text = self._ptyprocess.read()
                    self.iscreen.feed(text)
                except EOFError:
                    pass

    def wait_until(self, condition_function, timeout=None):
        if timeout is None:
            timeout = 10.0

        if self.running:
            start_time = time.time()

            while True:
                self._read()

                if condition_function(self.iscreen):
                    return

                if time.time() - start_time > timeout:
                    raise exceptions.IProcessTimeout(
                        "Timed out after {0} seconds:\n\n{1}".format(
                            timeout,
                            stripshot(self.iscreen.text),
                        )
                    )

                if not self.running:
                    self._read()
                    raise exceptions.UnexpectedExit(
                        self.exit_code,
                        stripshot(self.iscreen.text),
                    )
        else:
            raise exceptions.AlreadyExited(
                self.exit_code,
                stripshot(self.iscreen.text),
            )

    def wait_until_output_contains(self, text, timeout=None):
        """
        Wait until the totality of the output of the process contains
        at least one instance of 'text'.
        """
        self.wait_until(
            lambda iscreen: text in iscreen.raw_bytes,
            timeout,
        )

    def wait_until_on_screen(self, text, timeout=None):
        """
        Waits until the text specified appears on the process's terminal
        screen.
        """

        def on_screen(iscreen):
            return len([line for line in iscreen.display if text in line]) > 0

        self.wait_until(on_screen, timeout)

    def send_keys(self, text):
        """
        Send keys to the terminal process.
        """
        if self.running:
            self._ptyprocess.write(text)
        else:
            if self.finished:
                raise exceptions.AlreadyExited(
                    self.exit_code,
                    stripshot(self.iscreen.text),
                )
            else:
                raise exceptions.UnexpectedExit(
                    self.exit_code,
                    stripshot(self.iscreen.text),
                )

    def screenshot(self):
        """
        Get a 'screenshot' of the terminal window of a running or finished
        process.

        Use stripshot() to clean the whitespace from the right and bottom.
        """
        self._read()
        return self.iscreen.text

    def stripshot(self):
        """
        Get a stripped screenshot of the terminal window of the running process.

        i.e. all of the whitepace to the right and bottom will be cut.
        """
        return stripshot(self.screenshot())

    def wait_for_finish(self, timeout=None):
        """
        Wait until the process has finished.
        """
        if timeout is None:
            timeout = 10.0

        start_time = time.time()

        while True:
            if not self._ptyprocess.isalive():
                self._read()
                self._ptyprocess.close()
                self.finished = True
                return

            time.sleep(0.01)

            if time.time() - start_time > timeout:
                self._read()
                raise exceptions.IProcessTimeout(
                    "Timed out after {0} seconds:\n\n{1}".format(
                        timeout,
                        stripshot(self.iscreen.text),
                    )
                )

    def wait_for_successful_exit(self, timeout=None):
        """
        Wait until the process exits successfully. Raises exception
        if the process is still open after timeout or it exits
        with an exit code other than 0.
        """
        self.wait_for_finish(timeout=timeout)

        # self._ptyprocess.wait()
        # assert self._ptyprocess.exitstatus is not None

        exit_status = self.exit_code

        if exit_status != 0:
            raise exceptions.ExitWithError(
                exit_status,
                stripshot(self.iscreen.text),
            )

        self.finished = True

    def kill(self):
        """
        Send a kill -9 to the process and all of its descendants.
        """
        self._read()

        if self.finished:
            raise exceptions.AlreadyExited(
                self.exit_code,
                stripshot(self.iscreen.text),
            )

        if self.running:
            try:
                self.psutil.kill()
            except psutil.NoSuchProcess:
                raise exceptions.AlreadyExited(
                    self.exit_code,
                    stripshot(self.iscreen.text),
                )
        else:
            raise exceptions.UnexpectedExit(
                self.exit_code,
                stripshot(self.iscreen.text),
            )
