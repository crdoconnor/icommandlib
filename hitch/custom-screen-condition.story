Custom Screen Condition:
  based on: icommandlib
  description: |
    In this example, customized functions are used
    to detect various screen terminal conditions.
    
    This is useful when you are waiting for something
    to appear on screen that you cannot check just
    by looking for a block of text.
  preconditions:
    files:
      favoritecolor.py: |
        import sys
        import time

        answer = input("favorite color:")

        with open("color.txt", "w") as handle:
            handle.write(answer)

        sys.exit(0)
    setup: |
      from code_that_does_things import *
      from icommandlib import ICommand
      from commandlib import python

      def check_for_favorite_color(screen):
          return "favorite color" in screen.text

      def check_with_error(screen):
          raise_example_exception()
          
      process = ICommand(python("favoritecolor.py")).with_timeout(0.5).run()
  variations:
    Check for favorite color:
      preconditions:
        code: |
          process.wait_until(check_for_favorite_color)
          process.send_keys("blue\n")
          process.wait_for_finish()
      scenario:
      - Run code
      - File contents will be:
          filename: color.txt
          text: blue

    Check with error:
      preconditions:
        code: |
          process.wait_until(check_with_error)
      scenario:
      - Raises exception:
          exception type: code_that_does_things.ExampleException
          message:
