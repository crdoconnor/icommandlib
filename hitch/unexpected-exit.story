Unexpected exit:
  based on: icommandlib
  description: |
    While waiting for a condition to occur, a command may exit
    unexpectedly. This will raise an UnexpectedExit exception.
  preconditions:
    files:
      exitunexpectedly.py: |
        import sys

        print("an error occurred in this program")

        sys.exit(1)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("exitunexpectedly.py")).run()

    - Exception is raised:
        command: process.wait_until_output_contains("some message that will never appear")
        exception: unexpectedly
