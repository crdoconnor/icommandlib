Timeout:
  based on: icommandlib
  about: |
    Every wait_for or wait_until command may, of
    course, be waiting for something that never occurs.

    By default every condition that waits follows
    a timeout.

    You can also specify a timeout directly on
    every wait condition.
  given:
    files:
      favoritecolor.py: |
        import time
        import sys
        import os

        # Write out pid of this process so we can check if it is still alive
        with open("favoritecolor.pid", "w") as handle:
            handle.write(str(os.getpid()))

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

        time.sleep(1.0)
    setup: |
      from icommandlib import ICommand
      from commandlib import python

      process = ICommand(python("favoritecolor.py")).run()
  variations:
    wait_until_output_contains:
      given:
        code: |
          process.wait_until_output_contains("favorite color:", timeout=0.5)
          process.send_keys("blue\n")
          process.wait_until_output_contains("favorite film:", timeout=0.5)
          process.send_keys("usual suspects\n")
          process.wait_until_output_contains("favorite country:", timeout=0.5)
      steps:
      - Raises Exception:
          exception type: icommandlib.exceptions.IProcessTimeout
          message: |-
            Timed out after 0.5 seconds:

            favorite color:blue
            blue
            favorite film:usual suspects
            usual suspects

    wait_until_on_screen:
      given:
        code: |
          process.wait_until_on_screen("favorite color:", timeout=0.5)
          process.send_keys("blue\n")
          process.wait_until_on_screen("favorite film:", timeout=0.5)
          process.send_keys("usual suspects\n")
          process.wait_until_on_screen("favorite country:", timeout=0.5)
      steps:
      - Raises Exception:
          exception type: icommandlib.exceptions.IProcessTimeout
          message: |-
            Timed out after 0.5 seconds:

            favorite color:blue
            blue
            favorite film:usual suspects
            usual suspects

    wait_for_finish:
      given:
        code: |
          process.wait_until_on_screen("favorite color:", timeout=0.5)
          process.send_keys("blue\n")
          process.wait_until_on_screen("favorite film:", timeout=0.5)
          process.send_keys("usual suspects\n")
          process.wait_until_on_screen("favorite country:", timeout=1.5)
          process.send_keys("france\n")
          process.wait_for_finish(timeout=0.5)
      steps:
      - Raises Exception:
          exception type: icommandlib.exceptions.IProcessTimeout
          message: |-
            Timed out after 0.5 seconds:

            favorite color:blue
            blue
            favorite film:usual suspects
            usual suspects
            favorite country:france
            france

      - Processes not alive:
          from_filenames:
          - favoritecolor.pid


    wait_for_successful_exit:
      given:
        code: |
          process.wait_until_on_screen("favorite color:", timeout=0.5)
          process.send_keys("blue\n")
          process.wait_until_on_screen("favorite film:", timeout=0.5)
          process.send_keys("usual suspects\n")
          process.wait_until_on_screen("favorite country:", timeout=1.5)
          process.send_keys("france\n")
          process.wait_for_successful_exit(timeout=0.5)
      steps:
      - Raises Exception:
          exception type: icommandlib.exceptions.IProcessTimeout
          message: |-
            Timed out after 0.5 seconds:

            favorite color:blue
            blue
            favorite film:usual suspects
            usual suspects
            favorite country:france
            france

      - Processes not alive:
          from_filenames:
          - favoritecolor.pid
