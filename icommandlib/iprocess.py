from icommandlib import messages as message
from icommandlib.run import IProcessHandle
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
        self._request_queue = queue.Queue()
        self._response_queue = queue.Queue()
        self._handle = threading.Thread(
            target=IProcessHandle,
            args=(icommand, self._request_queue, self._response_queue)
        )
        self._handle.start()

        self._running_process = self._expect_message(message.ProcessStartedMessage)

        self._pid = self._running_process._pid
        self._master_fd = self._running_process._stdin
        self._async_send = self._expect_message(message.AsyncSendMethodMessage)
        
        self.final_screenshot = None

    def _expect_message(self, of_kind):
        response = self._response_queue.get()
        if isinstance(response, message.ExceptionMessage):
            raise response.value
        if isinstance(response, message.TimeoutMessage):
            # On timeout, kill processes
            for descendant in self.psutil.children(recursive=True):
                  descendant.kill()
            self.psutil.kill()
            raise exceptions.IProcessTimeout(
                "Timed out after {0} seconds.".format(response.value)
            )
        if isinstance(response, message.ExitMessage):
            if of_kind != message.ExitMessage:
                raise exceptions.UnexpectedExit(
                    "\n\n{0}\n\nProcess unexpectedly exited with exit_code {1}".format(
                        response.value.screenshot.strip(),
                        response.value.exit_code,
                    )
                )
            else:
                self.final_screenshot = response.value.screenshot
        if not isinstance(response, of_kind):
            raise Exception(
                "Threading error expected {0} got {1}".format(
                    type(of_kind), type(of_kind)
                )
            )
        return response.value
    
    @property
    def pid(self):
        return self._pid
    
    @property
    def psutil(self):
        return psutil.Process(self._pid)

    def wait_until(self, condition_function):
        self._request_queue.put(message.Condition(
            condition_function
        ))
        self._async_send()
        self._expect_message(message.OutputMatched)

    def wait_until_output_contains(self, text):
        """
        Wait until the totality of the output of the process contains
        at least one instance of 'text'.
        """
        self.wait_until(
            lambda iscreen: text in iscreen.raw_bytes.decode('utf8')
        )

    def wait_until_on_screen(self, text):
        """
        Waits until the text specified appears on the process's terminal
        screen.
        """
        self.wait_until(
            lambda iscreen: len([line for line in iscreen.display if text in line]) > 0
        )

    def send_keys(self, text):
        """
        Send keys to the terminal process.
        """
        self._request_queue.put(message.KeyPresses(text.encode('utf8')))
        self._async_send()

    def screenshot(self):
        """
        Get a screenshot of the terminal window of the running process.
        """
        self._request_queue.put(message.TakeScreenshot())
        self._async_send()
        return self._expect_message(message.Screenshot)

    def wait_for_finish(self):
        """
        Wait until the process has closed. Raises exception if
        the process is still open after timeout.
        """
        self._expect_message(message.ExitMessage)
    
    def wait_for_successful_exit(self):
        """
        Wait until the process exits successfully. Raises exception
        if the process is still open after timeout or it exits
        with an exit code other than 0.
        """
        response = self._expect_message(message.ExitMessage)

        if response.exit_code != 0:
            raise exceptions.ExitWithError(
                response.exit_code,
                response.screenshot.rstrip(),
            )
        
        return response

    def kill(self):
        for descendant in self.psutil.children(recursive=True):
              descendant.kill()
        self.psutil.kill()
        self.wait_for_finish()
