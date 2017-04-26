Prompt:
  based on: icommandlib
  preconditions:
    files:
      interactivecmd.py: |
        import sys

        answer = raw_input("command prompt:")
        sys.stdout(answer)
        sys.exit(0)
      example.py: |
        from icommandlib import ICommand
        from commandlib import python

        def run():
            process = ICommand(python("interactivecmd.py")).run()
            process.wait_for("command prompt:")
            process.send_keys("password\n")
            process.wait_for_close()
  scenario:
    - Run: |
        from example import run

        run()
