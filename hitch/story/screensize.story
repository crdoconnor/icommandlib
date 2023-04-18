Screensize:
  docs: screensize
  based on: icommandlib
  about: |
    You can run an interactive command in a terminal with a screen
    size of your choice.

    The default is a width of 80 and a height of 24.
  given:
    files:
      helloworld.py: |
        import time
        for _ in range(150):
            print("hello world")

        print("goodbye world")
        time.sleep(1)
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

  variations:
    Shrunken:
      given:
        code: |
          process = ICommand(python("favoritecolor.py")).screensize(5, 10).run()
          process.wait_until_output_contains("favorite color:")
          process.send_keys("red\n")
          process.wait_until_output_contains("RED")

          with open("screenshot.txt", "w") as handle:
              handle.write(process.screenshot())

          process.wait_for_finish()
      steps:
      - Run code
      - File contents should be:
          filename: screenshot.txt
          stripped: |-
            favor
            ite c
            olor:
            red
            RED
          height: 10
          width: 5

    Expanded:
      given:
        code: |
          process = ICommand(python("helloworld.py")).screensize(80, 160).run()
          process.wait_until_output_contains("goodbye world")

          with open("screenshot.txt", "w") as handle:
              handle.write(process.screenshot())

          process.wait_for_finish()
      steps:
      - Run code
      - File contents should be:
          filename: screenshot.txt
          stripped: |-
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            hello world
            goodbye world
          height: 160
          width: 80
