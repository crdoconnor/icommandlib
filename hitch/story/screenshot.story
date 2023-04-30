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
      from icommandlib import ICommand, IProcessTimeout
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

    Waiting for stripshot to match string and succeeding:
      given:
        code: |
          process.wait_for_stripshot_to_match("favorite color:red\nRED")
          process.wait_for_finish()
      steps:
      - Run code


    Waiting for stripshot to match string and failing:
      given:
        setup: |
          from icommandlib import ICommand, IProcessTimeout
          from commandlib import python

          process = ICommand(python("favoritecolor.py")).run()
          process.wait_until_output_contains("favorite color:")
        code: |
          try:
              process.wait_for_stripshot_to_match("notthis", timeout=0.1)
          except IProcessTimeout as error:
              with open("timeout-stripshot.txt", "w") as handle:
                  handle.write("Did not match. This was the output instead:\n")
                  handle.write(error.stripshot)
      steps:
      - Run code
      - File contents should be:
          filename: timeout-stripshot.txt
          stripped: |-
            Did not match. This was the output instead:
            favorite color:
          height: 2
          width: 43
