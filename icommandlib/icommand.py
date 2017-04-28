import commandlib
import pyte
import subprocess
import os
import pty
import select
import psutil


class IProcess(object):
    def __init__(self, process, master, stream, screen):
        self._process = process
        self._master = master
        self._stream = stream
        self._screen = screen

    @property
    def pid(self):
        return self._process.pid

    @property
    def psutil(self):
        return psutil.Process(self.pid)

    def _output_chunk(self):
        try:
            rlist, _wlist, _xlist = select.select([self._master], [], [], 1)
        except (KeyboardInterrupt, ):
            return None
        else:
            for fd in rlist:
                if fd is self._master:
                    out = os.read(self._master, 1024)
                    if not out:
                        return None
                    self._stream.feed(out.decode('utf8'))
        return out.decode('utf8')

    def wait_until_on_screen(self, text):
        while True:
            if self._output_chunk():
                for line in self._screen.display:
                    if text in line:
                        return

    def wait_until_output_contains(self, text):
        while True:
            if text in self._output_chunk():
                return

    def send_keys(self, text):
        os.write(self._master, text.encode('utf8'))

    def wait_for_finish(self):
        self.psutil.wait()

    def screenshot(self):
        return "\n".join(line for line in self._screen.display)


class ICommand(object):
    def __init__(self, command):
        assert isinstance(command, commandlib.Command), "must be type 'commandlib.Command'"
        self._command = command

    def run(self):
        master, slave = pty.openpty()
        stream = pyte.Stream()
        screen = pyte.Screen(80, 24)
        stream.attach(screen)
        proc = subprocess.Popen(
            self._command.arguments,
            bufsize=0,  # Ensures that all stdout/err is pushed to us immediately.
            stdout=slave,
            stderr=slave,
            stdin=slave,
            env=self._command.env,
        )
        return IProcess(proc, master, stream, screen)
