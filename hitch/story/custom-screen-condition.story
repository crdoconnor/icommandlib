Custom Screen Condition:
  docs: custom-screen-condition
  based on: icommandlib
  about: |
    In this example, customized functions are used
    to detect various screen terminal conditions.

    This is useful when you are waiting for something
    to appear on screen that you cannot check just
    by looking for a block of text.
  given:
    files:
      favoritecolor.py: |
        import sys
        import time

        answer = input("favorite color:")

        with open("color.txt", "w") as handle:
            handle.write(answer)

        sys.exit(0)
    setup: |
      from icommandlib import ICommand
      from commandlib import python
      
      class ExampleException(Exception):
            """
            This is a demonstration exception's docstring.

            It spreads across multiple lines.
            """
            pass

      def check_for_favorite_color(screen):
          return "favorite color" in screen.text

      def check_with_error(screen):
          raise ExampleException()
          
      process = ICommand(python("favoritecolor.py")).run()
  variations:
    Check for favorite color:
      given:
        code: |
          process.wait_until(check_for_favorite_color)
          process.send_keys("blue\n")
          process.wait_for_finish()
      steps:
      - Run code
          
      - File contents should be:
          filename: color.txt
          stripped: blue
          height: 1
          width: 4

    Check with error:
      given:
        code: |
          process.wait_until(check_with_error)
      steps:
      - Raises exception:
          exception type: __main__.ExampleException

    Wait until when program finished:
      given:
        code: |
          process.wait_until(check_for_favorite_color)
          process.send_keys("blue\n")
          process.wait_for_finish()
          process.wait_until(check_for_favorite_color)
      steps:
      - Raises exception:
          exception type: icommandlib.exceptions.AlreadyExited
          message: |-
            Process already exited with 0. Output:
            favorite color:blue
