Screenshot:
  based on: icommandlib
  description: |
    At any point during a program's execution, you should
    be able to take a screenshot of what appears on its
    virtual terminal.
  preconditions:
    files:
      favoritecolor.py: |
        import sys

        answer = input("favorite color:")

        sys.stdout.write(answer.upper())
        sys.stdout.flush()
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).run()
        process.wait_until_output_contains("favorite color:")
        process.send_keys("red\n")

        process.wait_until_output_contains("RED")

        with open("screenshot.txt", "w") as handle:
            handle.write(process.screenshot())

        process.wait_for_finish()

    - File contents will be:
        filename: screenshot.txt
        reference: screenshot
