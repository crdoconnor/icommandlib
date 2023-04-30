---
title: ICommandlib
---



<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/crdoconnor/icommandlib?style=social"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/icommandlib">

Icommandlib is an interactive command line runner, designed (unlike pexpect) to be able to run command line applications in a virtual terminal window and take screenshots.

It was designed for building self rewriting, documentation generating tests [like this](https://github.com/hitchdev/hitchstory/tree/master/examples/commandline)
for interactive command line apps with the [hitchstory framework](/hitchstory).

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

```
favorite color:red
Your favorite color is red
favorite movie:the usual suspects
Your favorite color is the usual suspects
```







## Install

```bash
$ pip install icommandlib
```

## Using ICommandLib

- [Custom Screen Condition](using/custom-screen-condition)
- [Kill](using/kill)
- [Process properties](using/process-properties)
- [Screenshot](using/screenshot)
- [Screensize](using/screensize)
- [Send keys](using/send-keys)
- [Wait until successful exit](using/wait-until-successful-exit)

