---
title: Send keys
---



In this example, favoritecolor.py is the program
which we are trying to interact with. It prompts twice
- for favorite color and favorite movie and writes
the answers to two different files.

Interacting with this requires waiting for the message
to appear, mimicking typing, waiting again and typing
again.






favoritecolor.py:

```python
import sys
import time

answer = input("favorite color:")

with open("color.txt", "w") as handle:
    handle.write(answer)

answer = input("favorite movie:")

with open("movie.txt", "w") as handle:
    handle.write(answer)

time.sleep(0.2)
sys.exit(0)
```

With code:

```python
from icommandlib import ICommand
from commandlib import python
import time

process = ICommand(python("favoritecolor.py")).run()
process.wait_until_output_contains("favorite color:")
process.send_keys("red\n")
process.wait_until_output_contains("favorite movie:")
process.send_keys("the usual suspects\n")
process.wait_until_on_screen("favorite color")

```




## Successful




```python
process.wait_for_successful_exit()

```



* When the code is run to completion.

The file contents of `color.txt` will then be:

```
red
```

The file contents of `movie.txt` will then be:

```
the usual suspects
```


## Already exited




```python
process.wait_for_successful_exit()

# We should have already known that the process would be finished
process.send_keys("oops")

```



Will raise an exception of type `icommandlib.exceptions.AlreadyExited`
with message:

```
Process already exited with 0. Output:
favorite color:red
favorite movie:the usual suspects
```


## After unexpected exit




```python
time.sleep(0.5)

# We didn't necessarily know that the process finished but it did
process.send_keys("oops")

```



Will raise an exception of type `icommandlib.exceptions.UnexpectedExit`
with message:

```
Process unexpectedly exited with exit code 0. Output:
favorite color:red
favorite movie:the usual suspects
```







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/send-keys.story">send-keys.story
    storytests.</a>

