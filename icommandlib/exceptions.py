from icommandlib.utils import stripshot


class ICommandError(Exception):
    pass


class IProcessTimeout(ICommandError):
    pass


class UnexpectedExit(ICommandError):
    pass


class IProcessExitError(ICommandError):
    MESSAGE = u"Process had non-zero exit code '{exit_code}'. Output:\n{screenshot}"

    def __init__(self, exit_code, screenshot):
        self.exit_code = exit_code
        self.screenshot = screenshot

        super(IProcessExitError, self).__init__(
            self.MESSAGE.format(
                exit_code=self.exit_code,
                screenshot=stripshot(self.screenshot)
            )
        )


class AlreadyExited(IProcessExitError):
    MESSAGE = u"Process already exited with '{exit_code}'. Output:\n{screenshot}"


class ExitWithError(IProcessExitError):
    pass
