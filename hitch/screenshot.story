Screenshot:
  based on: icommandlib
  description: |
    At any point during program execution, you should
    be able to take a screenshot of what appears on its
    virtual terminal.
  preconditions:
    files:
      favoritecolor.py: |
        import sys

        answer = input("favorite color:")

        sys.stdout.write(answer.upper())
        sys.stdout.flush()
    setup: |
      from icommandlib import ICommand
      from commandlib import python

      process = ICommand(python("favoritecolor.py")).run()
    code: |
      process.wait_until_output_contains("favorite color:")
      process.send_keys("red\n")

      process.wait_until_output_contains("RED")

      with open("screenshot.txt", "w") as handle:
          handle.write(process.screenshot())

      process.wait_for_finish()
      
      with open("finalscreenshot.txt", "w") as handle:
          handle.write(process.final_screenshot)
  scenario:
    - Run code
    - File contents will be:
        filename: screenshot.txt
        reference: screenshot
    - File contents will be:
        filename: finalscreenshot.txt
        reference: finalscreenshot
