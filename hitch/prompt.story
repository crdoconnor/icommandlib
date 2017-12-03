Send keys:
  based on: icommandlib
  description: |
    In this example, favoritecolor.py is the program
    which we are trying to interact with. It prompts twice
    - for favorite color and favorite movie and writes
    the answers to two different files.

    Interacting with this requires waiting for the message
    to appear, mimicking typing, waiting again and typing
    again.
  given:
    files:
      favoritecolor.py: |
        import sys
        import time

        answer = input("favorite color:")

        with open("color.txt", "w") as handle:
            handle.write(answer)

        answer = input("favorite movie:")

        with open("movie.txt", "w") as handle:
            handle.write(answer)

        time.sleep(0.2)
        sys.exit(0)
    setup: |
      from icommandlib import ICommand
      from commandlib import python
      import time

      process = ICommand(python("favoritecolor.py")).run()
      process.wait_until_output_contains("favorite color:")
      process.send_keys("red\n")
      process.wait_until_output_contains("favorite movie:")
      process.send_keys("the usual suspects\n")
      process.wait_until_on_screen("favorite color")
  variations:
    Successful:
      given:
        code: |
          process.wait_for_successful_exit()
      steps:
      - Run code
      - File contents will be:
          filename: color.txt
          text: red
      - File contents will be:
          filename: movie.txt
          text: the usual suspects

    Already exited:
      given:
        code: |
          process.wait_for_successful_exit()

          # We should have already known that the process would be finished
          process.send_keys("oops")
      steps:
      - Raises exception:
          exception type: icommandlib.exceptions.AlreadyExited
          message: |-
            Process already exited with '0'. Output:
            favorite color:red
            favorite movie:the usual suspects


    After unexpected exit:
      given:
        code: |
          time.sleep(0.5)

          # We didn't necessarily know that the process finished but it did
          process.send_keys("oops")
      steps:
      - Raises exception:
          exception type: icommandlib.exceptions.UnexpectedExit
          message: |2-


            favorite color:red                                                              
            favorite movie:the usual suspects

            Process unexpectedly exited with exit_code 0
