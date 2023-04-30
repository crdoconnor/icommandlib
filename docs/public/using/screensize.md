---
title: Screensize
---



You can run an interactive command in a terminal with a screen
size of your choice.

The default is a width of 80 and a height of 24.






helloworld.py:

```python
import time
for _ in range(150):
    print("hello world")

print("goodbye world")
time.sleep(1)
```
favoritecolor.py:

```python
import sys
import time

answer = input("favorite color:")

sys.stdout.write(answer.upper())
sys.stdout.flush()
time.sleep(1)
```

With code:

```python
from icommandlib import ICommand
from commandlib import python

```




## Shrunken




```python
process = ICommand(python("favoritecolor.py")).screensize(5, 10).run()
process.wait_until_output_contains("favorite color:")
process.send_keys("red\n")
process.wait_until_output_contains("RED")

with open("screenshot.txt", "w") as handle:
    handle.write(process.screenshot())

process.wait_for_finish()

```



* When the code is run to completion.

The file contents of `screenshot.txt` will then be:

```
favor
ite c
olor:
red
RED
```


## Expanded




```python
process = ICommand(python("helloworld.py")).screensize(80, 160).run()
process.wait_until_output_contains("goodbye world")

with open("screenshot.txt", "w") as handle:
    handle.write(process.screenshot())

process.wait_for_finish()

```



* When the code is run to completion.

The file contents of `screenshot.txt` will then be:

```
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
hello world
goodbye world
```







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/screensize.story">screensize.story
    storytests.</a>

