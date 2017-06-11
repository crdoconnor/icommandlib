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
        self._width = 80
        self._height = 24

    @property
    def timeout(self):
        return self._timeout

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def with_timeout(self, value):
        """
        Make the command time out after 'value' seconds.
        """
        assert type(value) is float, "timeout value must be a float"
        new_icommand = copy(self)
        new_icommand._timeout = value
        return new_icommand

    def screensize(self, width, height):
        """
        Make the interactive command run in a terminal of
        size width x height.
        """
        assert type(width) is int
        assert type(height) is int
        new_icommand = copy(self)
        new_icommand._width = width
        new_icommand._height = height
        return new_icommand

    def run(self):
        return iprocess.IProcess(self)
