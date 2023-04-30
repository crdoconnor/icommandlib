# Changelog


### 0.7.0

* FEATURE : Added wait for stripshot.


### 0.6.1

* FEATURE : Remove sleeps and speed things up.
* BUGFIX : Fix setup.py issues.
* FEATURE : Swap out pyenv for ptyprocess.


### 0.5.0

* FEATURE : Timeouts on wait_for_successful_exit and wait_for_exit.


### 0.4.2

* BUGFIX : Undo 'make controlling tty' bugfix.
* BUGFIX : Make icommandlib set up tty correctly.


### 0.4.0

* MINOR BUGFIX : When 'running', 'exit_code' and 'pid' properties are queried, make sure that they return the correct values each time.
* MAJOR REFACTOR : Stop the timeout exception from killing processes. If that's wanted, the user can do that themselves.
* MAJOR REFACTOR : IProcess now has exit_code.


### 0.3.0

* MINOR BUGFIX : If the program exited in an expected way before calling kill, raise AlreadyExited.
* MINOR BUGFIX : When send_keys is used at invalid times, raise sensible errors.
* PATCH : REFACTOR : Clarified some variable names.
* MINOR : BUGFIX : When screenshotting after a process has finished simply show the final screenshot.
* PATCH : REFACTOR : Renamed run -> handle.
* MINOR : BUGFIX : Throw proper exception when program has already exited when waiting for a condition.


### 0.2.0

* MAJOR : REFACTOR : Change where timeouts are set - now on waits only.


### 0.1.2

* PATCH FEATURE : Handle SIGINT and SIGKILL iprocesses and their children when received.
* MINOR : Handle SIGTERM by killing the process and subprocesses.
* FEATURE : On timeout, ensure process and subprocesses are killed.

