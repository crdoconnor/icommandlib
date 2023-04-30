from icommandlib.utils import stripshot


class ICommandError(Exception):
    pass


class IProcessTimeout(ICommandError):
    MESSAGE = "Timed out after {timeout} seconds:\n\n{stripshot}"

    def __init__(self, timeout, stripshot):
        self.timeout = timeout
        self.stripshot = stripshot

        super(IProcessTimeout, self).__init__(
            self.MESSAGE.format(
                timeout=self.timeout,
                stripshot=self.stripshot,
            )
        )


class IProcessExitError(ICommandError):
    def __init__(self, exit_code, screenshot):
        self.exit_code = exit_code
        self.screenshot = screenshot

        super(IProcessExitError, self).__init__(
            self.MESSAGE.format(
                exit_code=self.exit_code, screenshot=stripshot(self.screenshot)
            )
        )


class UnexpectedExit(IProcessExitError):
    MESSAGE = (
        "Process unexpectedly exited with "
        "exit code {exit_code}. Output:\n{screenshot}"
    )


class AlreadyExited(IProcessExitError):
    MESSAGE = "Process already exited with {exit_code}. " "Output:\n{screenshot}"


class ExitWithError(IProcessExitError):
    MESSAGE = (
        "Process exited with non-zero exit code {exit_code}. " "Output:\n{screenshot}"
    )
