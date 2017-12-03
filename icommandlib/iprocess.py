from icommandlib import messages as message
from icommandlib.handle import IProcessHandle
from icommandlib.utils import stripshot
from icommandlib import exceptions
import threading
import psutil
import queue


class IProcess(object):
    """
    An interactive process.

        Start process by initializing with an commandlib.Command object.
    """
    def __init__(self, icommand):
        self._icommand = icommand
        self._order_queue = queue.Queue()
        self._response_queue = queue.Queue()
        self._handle = threading.Thread(
            target=IProcessHandle,
            args=(icommand, self._order_queue, self._response_queue)
        )
        self._handle.start()

        self._running_process = self._wait_for_message(message.ProcessStartedMessage)

        self._pid = self._running_process._pid
        self._master_fd = self._running_process._stdin
        self._async_send = self._wait_for_message(message.AsyncSendMethodMessage)

        self._final_screenshot = None
        self._running = True

    def _check_messages(self):
        try:
            response = self._response_queue.get(block=False)
        except queue.Empty:
            response = None

        if response is not None:
            return self._deal_with_message(response)

    def _deal_with_message(self, response, of_kind=None):
        if isinstance(response, message.ExceptionMessage):
            raise response.value
        if isinstance(response, message.TimeoutMessage):
            # On timeout, kill processes
            for descendant in self.psutil.children(recursive=True):
                descendant.kill()
            self.psutil.kill()
            raise exceptions.IProcessTimeout(
                "Timed out after {0} seconds:\n\n{1}".format(
                    response.after,
                    stripshot(response.screenshot),
                )
            )
        if isinstance(response, message.ExitMessage):
            self._running = False
            if of_kind != message.ExitMessage:
                raise exceptions.UnexpectedExit(
                    response.value.exit_code,
                    response.value.screenshot,
                )
            else:
                self._exit_code = response.value.exit_code
                self._final_screenshot = response.value.screenshot
        if not isinstance(response, of_kind):
            raise Exception(
                "Threading error expected {0} got {1}".format(
                    type(of_kind), type(of_kind)
                )
            )
        return response.value

    def _wait_for_message(self, of_kind):
        response = self._response_queue.get()
        return self._deal_with_message(response, of_kind=of_kind)

    @property
    def pid(self):
        # FIXME: Check messages first, process may have finished unexpectedly
        return self._pid

    @property
    def running(self):
        # FIXME: Check messages first, process may have finished
        return self._running

    @property
    def psutil(self):
        """
        Return psutil.Process object from current process,
        if psutil is installed.
        """
        return psutil.Process(self._pid)

    def wait_until(self, condition_function, timeout=None):
        if self._running:
            self._check_messages()
            self._order_queue.put(message.Condition(
                condition_function, timeout
            ))
            self._async_send()
            self._wait_for_message(message.OutputMatched)
        else:
            raise exceptions.AlreadyExited(
                self._exit_code,
                self._final_screenshot,
            )

    def wait_until_output_contains(self, text, timeout=None):
        """
        Wait until the totality of the output of the process contains
        at least one instance of 'text'.
        """
        self.wait_until(
            lambda iscreen: text in iscreen.raw_bytes.decode('utf8'),
            timeout,
        )

    def wait_until_on_screen(self, text, timeout=None):
        """
        Waits until the text specified appears on the process's terminal
        screen.
        """
        def on_screen(iscreen):
            return len([
                line for line in iscreen.display if text in line
            ]) > 0

        self.wait_until(on_screen, timeout)

    def send_keys(self, text):
        """
        Send keys to the terminal process.
        """
        if self._running:
            self._check_messages()
            self._order_queue.put(message.KeyPresses(text.encode('utf8')))
            self._async_send()
        else:
            raise exceptions.AlreadyExited(
                self._exit_code,
                self._final_screenshot,
            )

    def screenshot(self):
        """
        Get a 'screenshot' of the terminal window of a running or finished
        process.

        Use stripshot() to clean the whitespace from the right and bottom.
        """
        if self._final_screenshot is not None:
            return self._final_screenshot
        else:
            self._order_queue.put(message.TakeScreenshot())
            self._async_send()
            return self._wait_for_message(message.Screenshot)

    def stripshot(self):
        """
        Get a stripped screenshot of the terminal window of the running process.

        i.e. all of the whitepace to the right and bottom will be cut.
        """
        return stripshot(self.screenshot())

    def wait_for_finish(self):
        """
        Wait until the process has finished.
        """
        self._wait_for_message(message.ExitMessage)

    def wait_for_successful_exit(self):
        """
        Wait until the process exits successfully. Raises exception
        if the process is still open after timeout or it exits
        with an exit code other than 0.
        """
        response = self._wait_for_message(message.ExitMessage)

        if response.exit_code != 0:
            raise exceptions.ExitWithError(
                response.exit_code,
                stripshot(response.screenshot),
            )

        return response

    def kill(self):
        """
        Send a kill -9 to the process and all of its descendants.
        """
        if self._running:
            self._check_messages()
            self._order_queue.put(message.KillProcess())
            self._async_send()
            self._wait_for_message(message.ProcessKilled)
        else:
            raise exceptions.AlreadyExited(
                self._exit_code,
                self._final_screenshot,
            )
