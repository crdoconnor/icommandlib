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
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        def check_for_favorite_color(screen):
            return "favorite color" in screen.text

        def check_with_error(screen):
            raise_example_exception()

    - Run: |
        process = ICommand(python("favoritecolor.py")).with_timeout(0.5).run()

    - Run: |
        process.wait_until(check_for_favorite_color)

    - Run: |
        process.send_keys("blue\n")
    
    - Run: |
        process.wait_for_finish()

    #- Sleep: 1

    - File contents will be:
        filename: color.txt
        text: blue

    - Run: |
        process = ICommand(python("favoritecolor.py")).run()

    - Exception is raised:
        command: process.wait_until(check_with_error)
        exception: ExampleException
