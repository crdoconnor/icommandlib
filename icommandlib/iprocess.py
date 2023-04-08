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
        if self.running:
            return None
        try:
            if self.psutil.status() == "zombie":
                self._ptyprocess.wait()
                return self._ptyprocess.exitstatus
        except psutil.NoSuchProcess:
            pass
        if self._ptyprocess.exitstatus is None:
            raise Exception(
                (
                    "This shouldn't happen. "
                    "Please raise bug at https://github.com/crdoconnor/icommandlib"
                )
            )
        return self._ptyprocess.exitstatus

    def _read(self):
        fd = self._ptyprocess.fd

        if fd != -1:
            readable, _, _ = select.select([fd], [], [], 0.01)

            if len(readable) != 0:
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
            self._read()

            if not self._ptyprocess.isalive():
                self._ptyprocess.close()
                self.finished = True
                return

            if time.time() - start_time > timeout:
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
