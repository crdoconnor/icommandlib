Screenshot:
  docs: screenshot
  based on: icommandlib
  about: |
    At any point during or after program execution, you can
    take a screenshot of what appears on its virtual terminal.
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
    Taking a screenshot:
      given:
        code: |
          with open("screenshot-before-finish.txt", "w") as handle:
              handle.write(process.screenshot())

          process.wait_for_finish()

          with open("stripshot-after-finish.txt", "w") as handle:
              handle.write(process.stripshot())
      steps:
      - Run code
      - File contents should be:
          filename: screenshot-before-finish.txt
          stripped: |-
            favorite color:red
            RED
          height: 24
          width: 80

      - File contents should be:
          filename: stripshot-after-finish.txt
          stripped: |-
            favorite color:red
            RED
          height: 2
          width: 18

    Waiting for stripshot to match string:
      given:
        code: |
          process.wait_for_stripshot_to_match("favorite color:red\nRED")
          process.wait_for_finish()
      steps:
      - Run code
