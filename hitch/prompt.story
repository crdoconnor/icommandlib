Prompt:
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

        with open("colors.txt", "w") as handle:
            handle.write(answer)

        sys.exit(0)
  scenario:
    - Run: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).run()
        process.wait_until_on_screen("favorite color:")
        process.send_keys("red")
        process.send_keys("\n")
        process.wait_for_finish()
    - File contents will be:
        filename: colors.txt
        text: red
