TTY:
  based on: icommandlib
  description: |
    Wait until the word 'hello' appears on
    the TTY.
  given:
    files:
      totty.sh: |
        echo hello > /dev/tty
    setup: |
      from icommandlib import ICommand
      from commandlib import Command

      process = ICommand(Command("./totty.sh")).run()
      process.wait_until_output_contains("hello")
      process.wait_for_finish()
  steps:
    - Run code
