class ICommandError(Exception):
    pass


class IProcessTimeout(ICommandError):
    pass
