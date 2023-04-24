# ICommandlib

[![Main branch status](https://github.com/crdoconnor/icommandlib/actions/workflows/regression.yml/badge.svg)](https://github.com/crdoconnor/icommandlib/actions/workflows/regression.yml)

Icommandlib is an interactive command line runner, designed (unlike pexpect) to be able to run command line applications in a virtual terminal window and take screenshots.

It was designed for building self rewriting, documentation generating tests [like this](https://github.com/hitchdev/hitchstory/tree/master/examples/commandline)
for interactive command line apps with the [hitchstory framework](https://hitchdev.com/icommandlib//hitchstory).

ICommandLib can take both terminal text screenshots and "stripshots" - terminal screenshots with all the white space to the right and bottom of the screen stripped.

## Example









favoritecolor.py:

```python
answer = input("favorite color:")
print(f"Your favorite color is {answer}")
answer = input("favorite movie:")
print(f"Your favorite color is {answer}")
```

With code:

```python
from icommandlib import ICommand
from commandlib import python
from pathlib import Path

process = ICommand(python("favoritecolor.py")).run()
process.wait_until_output_contains("favorite color:")
process.send_keys("red\n")
process.wait_until_output_contains("favorite movie:")
process.send_keys("the usual suspects\n")
process.wait_until_on_screen("favorite color")
process.wait_for_successful_exit()

Path("stripshot.txt").write_text(process.stripshot())

```





* When the code is run to completion.

The file contents of `stripshot.txt` will then be:

```favorite color:red
Your favorite color is red
favorite movie:the usual suspects
Your favorite color is the usual suspects```

With height 4 and width 41.







## Install

```bash
$ pip install icommandlib
```

## Using ICommandLib

- [Custom Screen Condition](https://hitchdev.com/icommandlib/using/custom-screen-condition)
- [Kill](https://hitchdev.com/icommandlib/using/kill)
- [Process properties](https://hitchdev.com/icommandlib/using/process-properties)
- [Screenshot](https://hitchdev.com/icommandlib/using/screenshot)
- [Screensize](https://hitchdev.com/icommandlib/using/screensize)
- [Send keys](https://hitchdev.com/icommandlib/using/send-keys)
- [Wait until successful exit](https://hitchdev.com/icommandlib/using/wait-until-successful-exit)

