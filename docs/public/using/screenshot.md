---
title: Screenshot
---



At any point during or after program execution, you can
take a screenshot of what appears on its virtual terminal.






favoritecolor.py:

```python
import sys

answer = input("favorite color:")

sys.stdout.write(answer.upper())
sys.stdout.flush()
```

With code:

```python
from icommandlib import ICommand
from commandlib import python

process = ICommand(python("favoritecolor.py")).run()
process.wait_until_output_contains("favorite color:")
process.send_keys("red\n")

process.wait_until_output_contains("RED")

```




## Taking a screenshot




```python
with open("screenshot-before-finish.txt", "w") as handle:
    handle.write(process.screenshot())

process.wait_for_finish()

with open("stripshot-after-finish.txt", "w") as handle:
    handle.write(process.stripshot())

```



* When the code is run to completion.

The file contents of `screenshot-before-finish.txt` will then be:

```favorite color:red
RED```

With height 24 and width 80.

The file contents of `stripshot-after-finish.txt` will then be:

```favorite color:red
RED```

With height 2 and width 18.


## Waiting for stripshot to match string




```python
process.wait_for_stripshot_to_match("favorite color:red\nRED")
process.wait_for_finish()

```



* When the code is run to completion.







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/screenshot.story">screenshot.story
    storytests.</a>

