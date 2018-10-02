

def stripshot(text):
    """
    Strips whitespace from right and bottom of
    a terminal screenshot.

    >>> stripshot(u'a\\nb\\n')
    'a\\nb'

    >>> stripshot(u'a   \\nb    \\n    \\n')
    'a\\nb'

    >>> stripshot(u'a   \\n     \\nc   \\n')
    'a\\n\\nc'
    """
    return u'\n'.join(
        line.rstrip() for line in text.split(u"\n") if line != u""
    ).rstrip()


"""
def pty_make_controlling_tty(tty_fd):

    This makes the pseudo-terminal the controlling tty. This should be
    more portable than the pty.fork() function. Specifically, this should
    work on Solaris.

    child_name = os.ttyname(tty_fd)

    # Disconnect from controlling tty. Harmless if not already connected.
    try:
        fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
        if fd >= 0:
            os.close(fd)
    except:
        # Already disconnected. This happens if running inside cron.
        pass

    # Verify we are disconnected from controlling tty
    # by attempting to open it again.
    try:
        fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
        if fd >= 0:
            os.close(fd)
            raise Exception('Failed to disconnect from ' +
                'controlling tty. It is still possible to open /dev/tty.')
    # which exception, shouldnt' we catch explicitly .. ?
    except:
        # Good! We are disconnected from a controlling tty.
        pass

    # Verify we can open child pty.
    fd = os.open(child_name, os.O_RDWR)
    if fd < 0:
        raise Exception("Could not open child pty, " + child_name)
    else:
        os.close(fd)

    # Verify we now have a controlling tty.
    fd = os.open("/dev/tty", os.O_WRONLY)
    if fd < 0:
        raise Exception("Could not open controlling tty, /dev/tty")
    else:
        os.close(fd)
"""

"""
#import array
#import fcntl
#import termios
#buf = array.array('h', [icommand.width, icommand.height, 0, 0])
#fcntl.ioctl(self.slave_fd, termios.TIOCSWINSZ, buf)
"""
