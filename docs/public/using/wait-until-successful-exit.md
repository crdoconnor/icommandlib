---
title: Wait until successful exit
---



Wait until exit with status code 0.






successful_exit.py:

```python
import sys
sys.stdout.write("hello")
sys.stdout.flush()
```
unsuccessful_exit.py:

```python
import sys
sys.stderr.write("something went wrong!")
sys.stderr.flush()
sys.exit(255)
```

With code:

```python
from icommandlib import ICommand
from commandlib import python

```




## Without errors




```python
process = ICommand(python("successful_exit.py")).run()
process.wait_for_successful_exit()

with open("finalscreenshot.txt", "w") as handle:
    handle.write(process.screenshot())

assert process.exit_code == 0, process.exit_code

```



* When the code is run to completion.

The file contents of `finalscreenshot.txt` will then be:

```
hello
```


## Unsuccessful exit




```python
ICommand(python("unsuccessful_exit.py")).run().wait_for_successful_exit()

```



Will raise an exception of type `icommandlib.exceptions.ExitWithError`
with message:

```
Process exited with non-zero exit code 255. Output:
something went wrong!
```







!!! note "Executable specification"

    Documentation automatically generated from 
    <a href="https://github.com/crdoconnor/icommandlib/blob/master/hitch/story/wait-until-successful-exit.story">wait-until-successful-exit.story
    storytests.</a>

