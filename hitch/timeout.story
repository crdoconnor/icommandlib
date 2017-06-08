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
        import time
        prompt = raw_input if sys.version_info.major == 2 else input

        time.sleep(0.3)

        answer = prompt("favorite color:")
        print(answer)

        time.sleep(0.3)
        answer = prompt("favorite film:")
        print(answer)

        time.sleep(1.0)
        answer = prompt("favorite country:")
        print(answer)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).with_timeout(0.5).run()

    - Run: |
        process.wait_until_output_contains("favorite color:")
        process.send_keys("blue\n")

    - Run: |
        process.wait_until_output_contains("favorite film:")
        process.send_keys("usual suspects\n")


    - Exception is raised:
        command: process.wait_until_output_contains("favorite country:")
        exception: Timed out after 0.5 seconds.
