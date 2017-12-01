Screenshot:
  based on: icommandlib
  description: |
    At any point during program execution, you should
    be able to take a screenshot of what appears on its
    virtual terminal.
    
    When the program finishes, it automatically takes
    a screenshot of the final state of the screen which
    is available in .final_screenshot.
  given:
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
      process.wait_until_output_contains("favorite color:")
      process.send_keys("red\n")

      process.wait_until_output_contains("RED")
  variations:
    Normal:
      given:
        code: |
          with open("screenshot-before-finish.txt", "w") as handle:
              handle.write(process.screenshot())

          process.wait_for_finish()
          
          with open("stripshot-after-finish.txt", "w") as handle:
              handle.write(process.stripshot())
      steps:
        - Run code
        - File contents will be:
            filename: screenshot-before-finish.txt
            reference: screenshot-before-finish
        - File contents will be:
            filename: stripshot-after-finish.txt
            reference: stripshot-after-finish
