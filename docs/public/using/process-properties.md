---
title: Process properties
---



Process properties can be queried at any time
and should reflect the current status of the process.






waiting.py:

```python
import time

time.sleep(0.1)
print("DONE!")
```

With code:

```python
from icommandlib import ICommand, UnexpectedExit
from commandlib import python
import time

process = ICommand(python("waiting.py")).run()

```




## Running

The 'running' property will report whether the
status is currently running or not.



```python
assert process.running == True
time.sleep(0.2)
assert process.running == False

```



* When the code is run to completion.


## Exit code

exit_code property will be None while the process
is running, and contain the exit code once finished.



```python
assert process.exit_code is None
time.sleep(0.2)
assert process.exit_code == 0, process.exit_code

```



* When the code is run to completion.


## Process ID

pid property contains the pid of the process while
the process is running, and None once it is finished.

If you try and get .pid after the process has finished
of its own accord, without having explicitly waited
for it, it will raise an UnexpectedExit exception.



```python
assert process.pid is not None
time.sleep(0.2)

try:
    now_finished = process.pid
except UnexpectedExit:
    pass

assert process.pid is None, process.pid

```



* When the code is run to completion.







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/process-properties.story">process-properties.story
    storytests.</a>

