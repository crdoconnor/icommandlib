class ICommandError(Exception):
    pass


class IProcessTimeout(ICommandError):
    pass


class UnexpectedExit(ICommandError):
    pass
