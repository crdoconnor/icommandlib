class ICommandError(Exception):
    pass


class IProcessTimeout(ICommandError):
    pass


class UnexpectedExit(ICommandError):
    pass


class ExitWithError(ICommandError):
    def __init__(self, exit_code, screenshot):
        self.exit_code = exit_code
        self.screenshot = screenshot
    
        super(ExitWithError, self).__init__((
            u"Process had non-zero exit code '{0}'. Output:\n{1}"
        ).format(
            self.exit_code,
            self.screenshot,
        ))
