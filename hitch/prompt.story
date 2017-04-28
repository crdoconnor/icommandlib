Prompts:
  based on: icommandlib
  description: |
    Plenty of simple CLI applications simply prompt the
    user for text and then do something simple. Interacting
    with these applications with icommandlib requires
    basic, single threaded commands.
  preconditions:
    files:
      favoritecolor.py: |
        import sys

        answer = input("favorite color:")

        with open("color.txt", "w") as handle:
            handle.write(answer)

        answer = input("favorite movie:")

        with open("movie.txt", "w") as handle:
            handle.write(answer)

        sys.exit(0)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).run()
        process.wait_until_output_contains("favorite color:")
        process.send_keys("red\n")
        process.wait_until_output_contains("favorite movie:")
        process.send_keys("the usual suspects\n")

    - Run: |
        # should still be on screen from before
        process.wait_until_on_screen("favorite color")
        process.wait_for_finish()
    - File contents will be:
        filename: color.txt
        text: red
    - File contents will be:
        filename: movie.txt
        text: the usual suspects
