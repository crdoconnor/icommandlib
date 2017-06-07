Prompts:
  based on: icommandlib
  description: |
    In this example, favoritecolor.py is the program
    which we are trying to interact with. It prompts twice
    - for favorite color and favorite movie and writes
    the answers to two different files.
    
    Interacting with this requires waiting for the message
    to appear, mimicking typing, waiting again and typing
    again.
  preconditions:
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

        time.sleep(0.5)
        sys.exit(0)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).run()

    - Run: |
        process.wait_until_output_contains("favorite color:")

    - Run: |
        process.send_keys("red\n")
        process.wait_until_output_contains("favorite movie:")

    - Run: |
        process.send_keys("the usual suspects\n")

    - Run: |
        # should still be on screen from before
        process.wait_until_on_screen("favorite color")
    
    - Run: |
        process.wait_for_finish()
    - File contents will be:
        filename: color.txt
        text: red
    - File contents will be:
        filename: movie.txt
        text: the usual suspects
