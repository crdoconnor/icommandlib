import commandlib
from copy import copy
from icommandlib import iprocess


class ICommand(object):
    """
    Represents an interactive command, built using the fluent interface.

    Using .run() will both start the command and return an IProcess.
    """
    def __init__(self, command):
        assert isinstance(command, commandlib.Command), "must be type 'commandlib.Command'"
        self._command = command
        self._timeout = None

    @property
    def timeout(self):
        return self._timeout

    def with_timeout(self, value):
        assert type(value) is float, "timeout value must be a float"
        new_icommand = copy(self)
        new_icommand._timeout = value
        return new_icommand

    def run(self):
        return iprocess.IProcess(self)
