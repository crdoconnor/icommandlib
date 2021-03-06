Unexpected exit:
  based on: icommandlib
  about: |
    While waiting for a condition to occur, a command may exit
    unexpectedly. This will raise an UnexpectedExit exception.
  given:
    files:
      exitunexpectedly.py: |
        import sys

        print("an error occurred in this program")

        sys.exit(1)
    setup: |
      from icommandlib import ICommand
      from commandlib import python
    code: |
      process = ICommand(python("exitunexpectedly.py")).run()
      process.wait_until_output_contains("some message that will never appear")
  steps:
  - Raises exception:
      exception type: icommandlib.exceptions.UnexpectedExit
      message: |-
        Process unexpectedly exited with exit code 1. Output:
        an error occurred in this program
