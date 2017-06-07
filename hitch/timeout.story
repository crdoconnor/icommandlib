Timeout:
  based on: icommandlib
  description: |
    Every wait_for or wait_until command may, of
    course, be waiting for something that never occurs.

    By default every condition waited for follows
    a timeout.
  preconditions:
    files:
      favoritecolor.py: |
        import sys
        import timeout

        time.sleep(1)

        answer = input("favorite color:")

        print(answer)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).with_timeout(0.5).run()

    - Exception is raised:
        command: process.wait_until_output_contains("favorite color:")
        exception: Timed out after 0.5 seconds.
