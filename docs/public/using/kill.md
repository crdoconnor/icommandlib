---
title: Kill
---



When an icommand is run, it is run in a separate process group. When it is killed,
the entire process group is killed.

For ordinary processes this changes nothing.

For processes that start child processes this means that their child processes
and their child processes are killed.






child.py:

```python
import os
import time

# Write out pid of this process so we can check if it is still alive
with open("child.pid", "w") as handle:
    handle.write(str(os.getpid()))

time.sleep(1)
```
parent.py:

```python
import os
import sys
import time
import subprocess

# Write out pid of this process so we can check if it is still alive
with open("parent.pid", "w") as handle:
    handle.write(str(os.getpid()))

# Run child.py with the same python used to run parent.py
subprocess.call([sys.executable, "child.py"])

# This process will get killed after 0.5 seconds by first
# test but exit on its own by second.
time.sleep(1)

print("I got to the end!")
```

With code:

```python
from icommandlib import ICommand
from commandlib import python
import time

```




## Normal




```python
process = ICommand(python("parent.py")).run()
time.sleep(0.5)
process.kill()

```



* When the code is run to completion.

Will result in the processes in these filenames
no longer being alive:


* parent.pid

* child.pid



## Died unexpectedly before kill




```python
process = ICommand(python("parent.py")).run()
time.sleep(2.5)
process.kill()

```



Will raise an exception of type `icommandlib.exceptions.UnexpectedExit`
with message:

```
Process unexpectedly exited with exit code 0. Output:
I got to the end!
```


## Expected finish before kill




```python
process = ICommand(python("parent.py")).run()
process.wait_for_successful_exit()
process.kill()

```



Will raise an exception of type `icommandlib.exceptions.AlreadyExited`
with message:

```
Process already exited with 0. Output:
I got to the end!
```







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/kill.story">kill.story
    storytests.</a>

