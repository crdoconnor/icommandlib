ICommandLib
===========

ICommandLib is a pythonic tool for interacting with interactive command line
applications.

It depends upon CommandLib, which is necessary for defining the commands
which you want to run.

ICommandLib is essentially a better version of pexpect:

* It has a cleaner, more functional API using a fluent interface.
* It runs the command using a virtual terminal (pyte), which lets you take screenshots.
* It asynchronously uses epoll (Linux) or kqueue (Mac/BSD) instead of select (using libuv/pyuv). See: https://stackoverflow.com/questions/17355593/why-is-epoll-faster-than-select

To install:

.. code-block:: sh

    $ pip install icommandlib
