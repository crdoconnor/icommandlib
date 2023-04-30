---
title: Custom Screen Condition
---



In this example, customized functions are used
to detect various screen terminal conditions.

This is useful when you are waiting for something
to appear on screen that you cannot check just
by looking for a block of text.






favoritecolor.py:

```python
import sys
import time

answer = input("favorite color:")

with open("color.txt", "w") as handle:
    handle.write(answer)

sys.exit(0)
```

With code:

```python
from icommandlib import ICommand
from commandlib import python

class ExampleException(Exception):
      """
      This is a demonstration exception's docstring.

      It spreads across multiple lines.
      """
      pass

def check_for_favorite_color(screen):
    return "favorite color" in screen.text

def check_with_error(screen):
    raise ExampleException()
    
process = ICommand(python("favoritecolor.py")).run()

```




## Check for favorite color




```python
process.wait_until(check_for_favorite_color)
process.send_keys("blue\n")
process.wait_for_finish()

```



* When the code is run to completion.

The file contents of `color.txt` will then be:

```
blue
```


## Check with error




```python
process.wait_until(check_with_error)

```



Will raise an exception of type `__main__.ExampleException`
with message:

```
None
```


## Wait until when program finished




```python
process.wait_until(check_for_favorite_color)
process.send_keys("blue\n")
process.wait_for_finish()
process.wait_until(check_for_favorite_color)

```



Will raise an exception of type `icommandlib.exceptions.AlreadyExited`
with message:

```
Process already exited with 0. Output:
favorite color:blue
```







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/custom-screen-condition.story">custom-screen-condition.story
    storytests.</a>

