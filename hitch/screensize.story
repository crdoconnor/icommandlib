Screensize:
  based on: icommandlib
  description: |
    You can run an interactive command in a screensize of your choice.
  given:
    files:
      favoritecolor.py: |
        import sys
        import time

        answer = input("favorite color:")

        sys.stdout.write(answer.upper())
        sys.stdout.flush()
        time.sleep(1)
    setup: |
        from icommandlib import ICommand
        from commandlib import python

        process = ICommand(python("favoritecolor.py")).screensize(5, 10).run()
    code: |
        process.wait_until_output_contains("favorite color:")
        process.send_keys("red\n")

        process.wait_until_output_contains("RED")

        with open("screenshot.txt", "w") as handle:
            handle.write(process.screenshot())

        process.wait_for_finish()

  steps:
    - Run code
    - File contents will be:
        reference: resized screenshot
        filename: screenshot.txt
