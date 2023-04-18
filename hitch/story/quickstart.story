Quickstart:
  based on: icommandlib
  given:
    files:
      favoritecolor.py: |
        answer = input("favorite color:")
        print(f"Your favorite color is {answer}")
        answer = input("favorite movie:")
        print(f"Your favorite color is {answer}")

    setup: |
      from icommandlib import ICommand
      from commandlib import python
      from pathlib import Path

      process = ICommand(python("favoritecolor.py")).run()
      process.wait_until_output_contains("favorite color:")
      process.send_keys("red\n")
      process.wait_until_output_contains("favorite movie:")
      process.send_keys("the usual suspects\n")
      process.wait_until_on_screen("favorite color")
      process.wait_for_successful_exit()
  
      Path("stripshot.txt").write_text(process.stripshot())
  steps:
  - Run code

  - File contents should be:
      filename: stripshot.txt
      stripped: |-
        favorite color:red
        Your favorite color is red
        favorite movie:the usual suspects
        Your favorite color is the usual suspects
      height: 4
      width: 41
